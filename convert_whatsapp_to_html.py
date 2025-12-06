#!/usr/bin/env python3
"""
WhatsApp Chat Beautifier
Converts WhatsApp _chat.txt to HTML
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from html import escape

# Language detection and system message filtering will use detected language

# Month names in multiple languages
MONTH_NAMES = {
    'en': ['January', 'February', 'March', 'April', 'May', 'June',
           'July', 'August', 'September', 'October', 'November', 'December'],
    'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
           'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
    'es': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
           'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    'fr': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
    'it': ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
           'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
}

def is_system_message(sender, content, lang='en'):
    """Detect if a message is a system message using detected language"""
    if '😎' in sender or 'WhatsApp' in sender:
        return True
    
    text_to_check = (sender + ' ' + content).lower()
    
    # Check keywords for the detected language first (most common case)
    lang_keywords = {
        'de': ['erstellt', 'hinzugefügt', 'geändert', 'verschlüsselt', 'gelöscht', 'weggelassen'],
        'en': ['created', 'added', 'changed', 'encrypted', 'deleted', 'omitted'],
        'es': ['creado', 'añadido', 'cambiado', 'cifrado', 'eliminado', 'omitido'],
        'fr': ['créé', 'ajouté', 'modifié', 'chiffré', 'supprimé', 'omis'],
        'it': ['creato', 'aggiunto', 'modificato', 'crittografato', 'eliminato', 'omesso']
    }
    
    # Check detected language keywords first
    if lang in lang_keywords:
        for keyword in lang_keywords[lang]:
            if keyword.lower() in text_to_check:
                return True
    
    # Fallback: check common system message patterns (covers edge cases)
    system_patterns = {
        'de': [r'du hast.*(erstellt|hinzugefügt|geändert|gelöscht)',
               r'diese nachricht (wurde gelöscht|wurde als admin gelöscht)'],
        'en': [r'you (created|added|changed|deleted)',
               r'has (created|added|changed|deleted)',
               r'this message (was deleted|has been deleted)'],
        'es': [r'has (creado|añadido|cambiado|eliminado)',
               r'este mensaje (fue eliminado|ha sido eliminado)'],
        'fr': [r'vous avez (créé|ajouté|modifié|supprimé)',
               r'ce message (a été supprimé|a été supprimé par un admin)'],
        'it': [r'hai (creato|aggiunto|modificato|eliminato)',
               r'questo messaggio (è stato eliminato|è stato eliminato da un amministratore)']
    }
    
    if lang in system_patterns:
        for pattern in system_patterns[lang]:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return True
    
    return False

def detect_language_from_content(messages):
    """Detect language from message content"""
    # Sample first 50 messages to detect language
    sample_text = ' '.join([msg.get('text', '') + ' ' + msg.get('sender', '') 
                            for msg in messages[:50]])
    sample_text = sample_text.lower()
    
    # Check for language indicators
    if any(word in sample_text for word in ['erstellt', 'hinzugefügt', 'geändert', 'gelöscht', 'du hast']):
        return 'de'  # German
    elif any(word in sample_text for word in ['created', 'added', 'changed', 'deleted', 'you have']):
        return 'en'  # English
    elif any(word in sample_text for word in ['creado', 'añadido', 'cambiado', 'eliminado']):
        return 'es'  # Spanish
    elif any(word in sample_text for word in ['créé', 'ajouté', 'modifié', 'supprimé']):
        return 'fr'  # French
    elif any(word in sample_text for word in ['creato', 'aggiunto', 'modificato', 'eliminato']):
        return 'it'  # Italian
    
    return 'en'  # Default to English

def parse_date(date_str):
    """Parse date string supporting both European (DD.MM.YY) and US (MM/DD/YY) formats"""
    # Try European formats first (DD.MM.YY or DD/MM/YY)
    european_formats = ['%d.%m.%y', '%d/%m/%y', '%d.%m.%Y', '%d/%m/%Y']
    # Then US formats (MM/DD/YY or MM.DD.YY)
    us_formats = ['%m/%d/%y', '%m.%d.%y', '%m/%d/%Y', '%m.%d.%Y']
    
    # Try all formats
    for fmt in european_formats + us_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # If all fail, try to auto-detect by checking if first number > 12
    parts = re.split(r'[\.\/]', date_str)
    if len(parts) >= 2:
        try:
            first = int(parts[0])
            second = int(parts[1])
            # If first > 12, it's likely DD.MM format (European)
            # If second > 12, it's likely MM.DD format (US)
            if first > 12 and second <= 12:
                # European format: DD.MM.YY
                for fmt in ['%d.%m.%y', '%d/%m/%y', '%d.%m.%Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            elif second > 12 and first <= 12:
                # US format: MM/DD/YY
                for fmt in ['%m/%d/%y', '%m.%d.%y', '%m/%d/%Y', '%m.%d.%Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
        except ValueError:
            pass
    
    return None

def format_date(date_str, lang='en'):
    """Convert date string to 'DD Month YYYY' format with language support"""
    dt = parse_date(date_str)
    if dt is None:
        return date_str
    
    months = MONTH_NAMES.get(lang, MONTH_NAMES['en'])
    return f"{dt.day} {months[dt.month - 1]} {dt.year}"

def parse_chat_file(chat_path):
    """Parse WhatsApp _chat.txt file"""
    messages = []
    current = None
    
    # Pattern for: [DD.MM.YY, HH:MM:SS] Sender: Message
    # Also handles: ‎[DD.MM.YY, HH:MM:SS] Sender: ‎<WORD: filename> (language-agnostic)
    # Note: The ‎ character (U+200E) is a left-to-right mark
    # We'll strip it first, then match
    pattern = r'^[‎\s\[]?(\d{1,2}[\.\/]\d{1,2}[\.\/]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)[\]\s]*[-:]?\s*([^:]+):\s*(.*)$'
    
    with open(chat_path, 'r', encoding='utf-8') as f:
        for line in f:
            original_line = line
            # Remove left-to-right mark (U+200E) and strip
            line = line.replace('\u200e', '').strip()
            if not line:
                if current:
                    # Empty line might indicate end of message, but we'll continue
                    pass
                continue
            
            match = re.match(pattern, line)
            
            if match:
                # Save previous message if exists
                if current:
                    messages.append(current)
                
                date_str = match.group(1)
                time_str = match.group(2)
                sender = match.group(3).strip()
                content = match.group(4).strip()
                
                # Check for media attachment - look for <WORD: filename> (language-agnostic)
                # Matches: <Anhang: ...>, <Attachment: ...>, <Anexo: ...>, etc.
                media_match = re.search(r'<([^:]+):\s*([^>]+)>', content)
                media_file = None
                media_type = None
                
                if media_match:
                    # Group 2 contains the filename
                    media_file = media_match.group(2).strip()
                    # Determine media type
                    if media_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        media_type = 'image'
                    elif media_file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                        media_type = 'video'
                    else:
                        media_type = 'file'
                    # Remove media tag and any leading/trailing whitespace/characters (language-agnostic)
                    content = re.sub(r'[‎\s]*<[^:]+:\s*[^>]+>[‎\s]*', '', content).strip()
                
                current = {
                    'date': date_str,
                    'time': time_str,
                    'sender': sender,
                    'text': content,
                    'media_file': media_file,
                    'media_type': media_type
                }
            elif current:
                # Continuation of previous message
                # But check if this line looks like a new message (starts with date pattern)
                if re.match(r'^[‎\[]?\d{1,2}[\.\/]', line):
                    # This looks like a new message that didn't match the full pattern
                    # Save current and try to parse this as a new message
                    messages.append(current)
                    current = None
                else:
                    # True continuation - append to text
                    if current['text']:
                        current['text'] += '\n' + line
                    else:
                        current['text'] = line
    
    if current:
        messages.append(current)
    
    # Combine media + text messages that have the same timestamp and sender
    # This handles cases where WhatsApp exports media and text as separate lines
    combined_messages = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        
        # Check if this is a media-only message (no text)
        if msg['media_file'] and (not msg['text'] or not msg['text'].strip()):
            # Check if next message is text-only from same sender with same timestamp
            if i + 1 < len(messages):
                next_msg = messages[i + 1]
                if (next_msg['sender'] == msg['sender'] and 
                    next_msg['date'] == msg['date'] and 
                    next_msg['time'] == msg['time'] and
                    not next_msg['media_file'] and 
                    next_msg['text'] and next_msg['text'].strip()):
                    # Combine: keep media from first, text from second
                    combined_msg = msg.copy()
                    combined_msg['text'] = next_msg['text']
                    combined_messages.append(combined_msg)
                    i += 2  # Skip both messages
                    continue
        
        combined_messages.append(msg)
        i += 1
    
    return combined_messages


def determine_own_sender(messages, lang='en'):
    """Determine which sender is 'own' (typically first non-phone-number sender)"""
    for msg in messages:
        sender = msg['sender']
        content = msg.get('text', '')
        # Skip system messages using detected language
        if is_system_message(sender, content, lang):
            continue
        # If sender doesn't start with + or isn't all digits, it's likely "own"
        if not sender.startswith('+') and not sender.replace(' ', '').isdigit():
            return sender
    return None

def generate_html(messages, folder_name, output_path):
    """Generate HTML matching modern WhatsApp-style structure"""
    
    # Detect language from content (including system messages - they help detect language!)
    lang = detect_language_from_content(messages)
    
    # Determine own sender using detected language
    own_sender = determine_own_sender(messages, lang)
    if not own_sender:
        # Fallback: use first non-system sender
        for msg in messages:
            if not is_system_message(msg['sender'], msg.get('text', ''), lang):
                own_sender = msg['sender']
                break
    
    # Extract chat title from first message with group emoji
    chat_title = folder_name.replace('_', ' ').replace('whatsapp chat ', '').title()
    if messages:
        # Look for the group chat name in the first messages
        for msg in messages[:5]:  # Check first 5 messages
            sender = msg['sender']
            if '😎' in sender:
                # Use the full sender name as chat title (includes emoji and name)
                chat_title = sender
                break
    
    # Get year range for subtitle
    years = set()
    for msg in messages:
        date_str = msg['date']
        dt = parse_date(date_str)
        if dt:
            years.add(dt.year)
    year_range = '/'.join(sorted(str(y) for y in years)) if years else ''
    
    # Count valid messages for footer
    valid_message_count = sum(1 for msg in messages 
                             if not is_system_message(msg['sender'], msg.get('text', ''), lang))
    
    
    # Generate conversation HTML
    conversation_html = []
    last_date = None
    last_sender = None
    last_is_own = None
    current_group_open = False
    
    for msg in messages:
        # Skip system messages using detected language
        if is_system_message(msg['sender'], msg.get('text', ''), lang):
            continue
        
        # Date separator - close any open group first
        date_formatted = format_date(msg['date'], lang)
        if date_formatted != last_date:
            if current_group_open:
                conversation_html.append(f'            </ol>')
                conversation_html.append(f'        </li>')
                current_group_open = False
            
            # Reset last_sender so next message always starts a new group
            last_sender = None
            last_is_own = None
            
            last_date = date_formatted
            conversation_html.append(f'        <li class="date-time">')
            conversation_html.append(f'            <p>{date_formatted}</p>')
            conversation_html.append(f'        </li>')
        
        # Determine if own or other
        is_own = msg['sender'] == own_sender
        msg_class = 'right' if is_own else 'left'
        
        # Message content
        has_text = msg['text'] and msg['text'].strip()
        has_media = msg['media_file'] is not None
        has_both = has_media and has_text
        
        # Always start a new message group for each message to avoid grouping
        # Close previous group if exists
        if current_group_open:
            conversation_html.append(f'            </ol>')
            conversation_html.append(f'        </li>')
        
        # Start new message group for this message
        conversation_html.append(f'        <li class="{msg_class}">')
        conversation_html.append(f'            <ol class="messages">')
        current_group_open = True
        
        # User name (show for both incoming and outgoing)
        conversation_html.append(f'                <li class="user-name">')
        conversation_html.append(f'                    <p>{escape(msg["sender"])}</p>')
        conversation_html.append(f'                </li>')
        
        if has_media:
            media_path = f'{folder_name}/{msg["media_file"]}'
            if msg['media_type'] == 'image':
                conversation_html.append(f'                <li class="message image">')
                conversation_html.append(f'                    <a class="shared" href="{media_path}">')
                conversation_html.append(f'                        <img class="img-shared" src="{media_path}">')
                conversation_html.append(f'                        <span class="zoom"></span>')
                conversation_html.append(f'                    </a>')
                # If text follows, don't show time on image, it will be on text
                if not has_text:
                    conversation_html.append(f'                    <span class="hours">{msg["time"]}</span>')
                conversation_html.append(f'                </li>')
            elif msg['media_type'] == 'video':
                conversation_html.append(f'                <li class="message video">')
                conversation_html.append(f'                    <a class="shared" href="{media_path}">')
                conversation_html.append(f'                        <p>{escape(msg["media_file"])}</p>')
                conversation_html.append(f'                    </a>')
                # If text follows, don't show time on video, it will be on text
                if not has_text:
                    conversation_html.append(f'                    <span class="hours">{msg["time"]}</span>')
                conversation_html.append(f'                </li>')
            else:
                conversation_html.append(f'                <li class="message file">')
                conversation_html.append(f'                    <p>{escape(msg["media_file"])}</p>')
                # If text follows, don't show time on file, it will be on text
                if not has_text:
                    conversation_html.append(f'                    <span class="hours">{msg["time"]}</span>')
                conversation_html.append(f'                </li>')
        
        if has_text:
            conversation_html.append(f'                <li class="message">')
            text = escape(msg['text']).replace('\n', '<br>')
            conversation_html.append(f'                    <p>{text}</p>')
            conversation_html.append(f'                    <span class="hours">{msg["time"]}</span>')
            conversation_html.append(f'                </li>')
        
        last_sender = msg['sender']
        last_is_own = is_own
    
    # Close last group
    if current_group_open:
        conversation_html.append(f'            </ol>')
        conversation_html.append(f'        </li>')
    
    conversation_html_str = '\n'.join(conversation_html)
    
    # Load CSS template
    css_template_path = Path(__file__).parent / 'style.css'
    if css_template_path.exists():
        css_template = css_template_path.read_text(encoding='utf-8')
    else:
        print("⚠️  Warning: style.css not found")
        css_template = None
    
    if not css_template:
        raise FileNotFoundError("style.css not found!")
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(chat_title)}</title>
<style type="text/css">
{css_template}
</style>
<script>
// Scroll buttons functionality
(function() {{
    const container = document.querySelector('ol.conversation');
    const scrollButtons = document.getElementById('scroll-buttons');
    const btnUp = document.getElementById('scroll-up');
    const btnDown = document.getElementById('scroll-down');
    
    if (!container || !scrollButtons) return;
    
    function updateScrollButtons() {{
        const scrollTop = container.scrollTop;
        const scrollHeight = container.scrollHeight;
        const clientHeight = container.clientHeight;
        
        if (btnUp) {{
            btnUp.classList.toggle('hidden', scrollTop <= 100);
        }}
        if (btnDown) {{
            btnDown.classList.toggle('hidden', scrollTop >= scrollHeight - clientHeight - 100);
        }}
    }}
    
    container.addEventListener('scroll', updateScrollButtons);
    updateScrollButtons();
    
    if (btnUp) {{
        btnUp.addEventListener('click', function() {{
            container.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});
    }}
    
    if (btnDown) {{
        btnDown.addEventListener('click', function() {{
            container.scrollTo({{ top: container.scrollHeight, behavior: 'smooth' }});
        }});
    }}
}})();

// Lightbox functionality for images and videos
(function() {{
    // Create lightbox element
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <button class="lightbox-close" aria-label="Close">×</button>
        <div class="lightbox-content"></div>
    `;
    document.body.appendChild(lightbox);
    
    const lightboxContent = lightbox.querySelector('.lightbox-content');
    const closeButton = lightbox.querySelector('.lightbox-close');
    
    function openLightbox(mediaUrl, isVideo) {{
        lightboxContent.innerHTML = '';
        
        if (isVideo) {{
            const video = document.createElement('video');
            video.src = mediaUrl;
            video.controls = true;
            video.autoplay = true;
            lightboxContent.appendChild(video);
        }} else {{
            const img = document.createElement('img');
            img.src = mediaUrl;
            lightboxContent.appendChild(img);
        }}
        
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }}
    
    function closeLightbox() {{
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
        // Stop video playback
        const video = lightboxContent.querySelector('video');
        if (video) {{
            video.pause();
            video.src = '';
        }}
    }}
    
    // Handle clicks on media links
    document.addEventListener('click', function(e) {{
        const link = e.target.closest('a.shared');
        if (!link) return;
        
        e.preventDefault();
        const mediaUrl = link.getAttribute('href');
        
        // Determine if it's a video or image
        const isVideo = /\.(mp4|mov|avi|mkv)$/i.test(mediaUrl);
        const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(mediaUrl);
        
        if (isVideo || isImage) {{
            openLightbox(mediaUrl, isVideo);
        }} else {{
            // For other file types, open in new tab
            window.open(mediaUrl, '_blank');
        }}
    }});
    
    // Close on close button click
    closeButton.addEventListener('click', function(e) {{
        e.stopPropagation();
        closeLightbox();
    }});
    
    // Close on lightbox background click
    lightbox.addEventListener('click', function(e) {{
        if (e.target === lightbox) {{
            closeLightbox();
        }}
    }});
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape' && lightbox.classList.contains('active')) {{
            closeLightbox();
        }}
    }});
}})();
</script>
</head>
<body>
<div id="wrapper">
    <header class="title">
        <div class="content">
            <div class="header-left">
                <div>
                    <h1>{escape(chat_title)}</h1>
                    {f'<p class="subtitle">{year_range}</p>' if year_range else ''}
                </div>
            </div>
        </div>
    </header>
    
    <ol class="conversation">
{conversation_html_str}
    </ol>
    
    <div id="scroll-buttons" class="scroll-buttons">
        <button id="scroll-up" class="scroll-button hidden" aria-label="Scroll to top">↑</button>
        <button id="scroll-down" class="scroll-button" aria-label="Scroll to bottom">↓</button>
    </div>
    
    <footer id="footer">
        <p>{valid_message_count} messages • Exported from WhatsApp</p>
    </footer>
</div>
</body>
</html>'''
    
    return html

def main():
    print("=" * 60)
    print("   WhatsApp Chat Beautifier")
    print("=" * 60)
    print()
    
    # Get folder path
    if len(sys.argv) > 1:
        folder_path = Path(sys.argv[1])
    else:
        folder_input = input("📁 Path to WhatsApp chat folder: ").strip()
        folder_path = Path(folder_input)
    
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"❌ Folder not found: {folder_path}")
        return
    
    # Find _chat.txt
    chat_file = folder_path / '_chat.txt'
    if not chat_file.exists():
        print(f"❌ _chat.txt not found in: {folder_path}")
        return
    
    print(f"✅ Folder found: {folder_path.name}")
    print(f"✅ Chat file found: {chat_file.name}")
    print()
    
    # Check for background.jpg
    background_jpg = folder_path / 'background.jpg'
    if not background_jpg.exists():
        # Check parent directory
        background_jpg = folder_path.parent / 'background.jpg'
        if not background_jpg.exists():
            print("⚠️  Warning: background.jpg not found. HTML will be created, but background is missing.")
    
    print("🔄 Processing chat...")
    
    try:
        # Parse messages
        messages = parse_chat_file(chat_file)
        print(f"✅ {len(messages)} messages parsed")
        
        if len(messages) == 0:
            print("❌ No messages found!")
            return
        
        # Generate HTML
        print("📝 Creating HTML...")
        folder_name = folder_path.name
        html = generate_html(messages, folder_name, folder_path)
        
        # Save HTML file in parent directory (same level as folder)
        output_path = folder_path.parent / f"{folder_name}_chat.html"
        output_path.write_text(html, encoding='utf-8')
        
        print()
        print("=" * 60)
        print(f"✅ DONE!")
        print(f"📄 Saved: {output_path}")
        print(f"💾 Size: {output_path.stat().st_size / 1024:.1f} KB")
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
