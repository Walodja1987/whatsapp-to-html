#!/usr/bin/env python3
"""
WhatsApp Chat Beautifier - CopyTrans Style
Converts WhatsApp _chat.txt to HTML matching CopyTrans format
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from html import escape

def parse_chat_file(chat_path):
    """Parse WhatsApp _chat.txt file"""
    messages = []
    current = None
    
    # Pattern for: [DD.MM.YY, HH:MM:SS] Sender: Message
    # Also handles: ‎[DD.MM.YY, HH:MM:SS] Sender: ‎<Anhang: filename>
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
                
                # Check for media attachment - look for <Anhang: filename>
                media_match = re.search(r'<Anhang:\s*([^>]+)>', content)
                media_file = None
                media_type = None
                
                if media_match:
                    media_file = media_match.group(1).strip()
                    # Determine media type
                    if media_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        media_type = 'image'
                    elif media_file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                        media_type = 'video'
                    else:
                        media_type = 'file'
                    # Remove media tag and any leading/trailing whitespace/characters
                    content = re.sub(r'[‎\s]*<Anhang:\s*[^>]+>[‎\s]*', '', content).strip()
                
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

def format_date(date_str):
    """Convert DD.MM.YY to 'DD Month YYYY' format"""
    try:
        # Try different date formats
        for fmt in ['%d.%m.%y', '%d/%m/%y', '%d.%m.%Y', '%d/%m/%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                # Format as "10 December 2022"
                months = ['January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December']
                return f"{dt.day} {months[dt.month - 1]} {dt.year}"
            except ValueError:
                continue
        return date_str
    except:
        return date_str

def determine_own_sender(messages):
    """Determine which sender is 'own' (typically first non-phone-number sender)"""
    for msg in messages:
        sender = msg['sender']
        # Skip system messages
        if '😎' in sender or 'WhatsApp' in sender or 'erstellt' in sender or 'hinzugefügt' in sender or 'geändert' in sender:
            continue
        # If sender doesn't start with + or isn't all digits, it's likely "own"
        if not sender.startswith('+') and not sender.replace(' ', '').isdigit():
            return sender
    return None

def generate_html(messages, folder_name, output_path):
    """Generate HTML matching modern WhatsApp-style structure"""
    
    # Determine own sender
    own_sender = determine_own_sender(messages)
    if not own_sender:
        # Fallback: use first non-system sender
        for msg in messages:
            if not any(x in msg['sender'] for x in ['😎', 'WhatsApp', 'erstellt', 'hinzugefügt', 'geändert']):
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
        for fmt in ['%d.%m.%y', '%d/%m/%y', '%d.%m.%Y', '%d/%m/%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                years.add(dt.year)
                break
            except ValueError:
                continue
    year_range = '/'.join(sorted(str(y) for y in years)) if years else ''
    
    # Count valid messages for footer
    valid_message_count = sum(1 for msg in messages 
                             if not any(x in msg['sender'] for x in ['😎', 'WhatsApp', 'erstellt', 'hinzugefügt', 'geändert', 'verschlüsselt']))
    
    
    # Generate conversation HTML
    conversation_html = []
    last_date = None
    last_sender = None
    last_is_own = None
    current_group_open = False
    
    for msg in messages:
        # Skip system messages
        if any(x in msg['sender'] for x in ['😎', 'WhatsApp', 'erstellt', 'hinzugefügt', 'geändert', 'verschlüsselt']):
            continue
        
        # Date separator - close any open group first
        date_formatted = format_date(msg['date'])
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
    print("   WhatsApp Chat Beautifier - Modern Style")
    print("=" * 60)
    print()
    
    # Get folder path
    if len(sys.argv) > 1:
        folder_path = Path(sys.argv[1])
    else:
        folder_input = input("📁 Pfad zum WhatsApp Chat-Ordner: ").strip()
        folder_path = Path(folder_input)
    
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"❌ Ordner nicht gefunden: {folder_path}")
        return
    
    # Find _chat.txt
    chat_file = folder_path / '_chat.txt'
    if not chat_file.exists():
        print(f"❌ _chat.txt nicht gefunden in: {folder_path}")
        return
    
    print(f"✅ Ordner gefunden: {folder_path.name}")
    print(f"✅ Chat-Datei gefunden: {chat_file.name}")
    print()
    
    # Check for background.jpg
    light_jpg = folder_path / 'background.jpg'
    if not light_jpg.exists():
        # Check parent directory
        light_jpg = folder_path.parent / 'background.jpg'
        if not light_jpg.exists():
            print("⚠️  Warnung: background.jpg nicht gefunden. HTML wird erstellt, aber Hintergrund fehlt.")
    
    print("🔄 Verarbeite Chat...")
    
    try:
        # Parse messages
        messages = parse_chat_file(chat_file)
        print(f"✅ {len(messages)} Nachrichten geparst")
        
        if len(messages) == 0:
            print("❌ Keine Nachrichten gefunden!")
            return
        
        # Generate HTML
        print("📝 Erstelle HTML...")
        folder_name = folder_path.name
        html = generate_html(messages, folder_name, folder_path)
        
        # Save HTML file in parent directory (same level as folder)
        output_path = folder_path.parent / f"{folder_name}_chat.html"
        output_path.write_text(html, encoding='utf-8')
        
        print()
        print("=" * 60)
        print(f"✅ FERTIG!")
        print(f"📄 Gespeichert: {output_path}")
        print(f"💾 Größe: {output_path.stat().st_size / 1024:.1f} KB")
        print()
        print("ℹ️  Wichtig: Die HTML-Datei muss im gleichen Verzeichnis")
        print(f"   wie der Ordner '{folder_name}' sein, damit die Bilder")
        print("   korrekt geladen werden können.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
