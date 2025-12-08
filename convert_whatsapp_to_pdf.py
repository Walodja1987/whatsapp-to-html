#!/usr/bin/env python3
"""
WhatsApp-To-PDF (Print-Ready HTML)
Converts WhatsApp _chat.txt to print-optimized HTML for browser PDF export
"""

import re
import sys
import webbrowser
from pathlib import Path
from datetime import datetime
from html import escape

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
    
    # Check keywords for the detected language
    lang_keywords = {
        'de': ['erstellt', 'hinzugefügt', 'geändert', 'verschlüsselt', 'gelöscht', 'weggelassen'],
        'en': ['created', 'added', 'changed', 'encrypted', 'deleted', 'omitted'],
        'es': ['creado', 'añadido', 'cambiado', 'cifrado', 'eliminado', 'omitido'],
        'fr': ['créé', 'ajouté', 'modifié', 'chiffré', 'supprimé', 'omis'],
        'it': ['creato', 'aggiunto', 'modificato', 'crittografato', 'eliminato', 'omesso']
    }
    
    if lang in lang_keywords:
        for keyword in lang_keywords[lang]:
            if keyword.lower() in text_to_check:
                return True
    
    # Fallback: check common system message patterns
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
    sample_text = ' '.join([msg.get('text', '') + ' ' + msg.get('sender', '') 
                            for msg in messages[:50]])
    sample_text = sample_text.lower()
    
    if any(word in sample_text for word in ['erstellt', 'hinzugefügt', 'geändert', 'gelöscht', 'du hast']):
        return 'de'
    elif any(word in sample_text for word in ['created', 'added', 'changed', 'deleted', 'you have']):
        return 'en'
    elif any(word in sample_text for word in ['creado', 'añadido', 'cambiado', 'eliminado']):
        return 'es'
    elif any(word in sample_text for word in ['créé', 'ajouté', 'modifié', 'supprimé']):
        return 'fr'
    elif any(word in sample_text for word in ['creato', 'aggiunto', 'modificato', 'eliminato']):
        return 'it'
    
    return 'en'

def parse_date(date_str):
    """Parse date string supporting both European (DD.MM.YY) and US (MM/DD/YY) formats"""
    european_formats = ['%d.%m.%y', '%d/%m/%y', '%d.%m.%Y', '%d/%m/%Y']
    us_formats = ['%m/%d/%y', '%m.%d.%y', '%m/%d/%Y', '%m.%d.%Y']
    
    for fmt in european_formats + us_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Auto-detect by checking if first number > 12
    parts = re.split(r'[\.\/]', date_str)
    if len(parts) >= 2:
        try:
            first = int(parts[0])
            second = int(parts[1])
            if first > 12 and second <= 12:
                for fmt in ['%d.%m.%y', '%d/%m/%y', '%d.%m.%Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            elif second > 12 and first <= 12:
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
    
    pattern = r'^[‎\s\[]?(\d{1,2}[\.\/]\d{1,2}[\.\/]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)[\]\s]*[-:]?\s*([^:]+):\s*(.*)$'
    
    with open(chat_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\u200e', '').strip()
            if not line:
                continue
            
            match = re.match(pattern, line)
            
            if match:
                if current:
                    messages.append(current)
                
                date_str = match.group(1)
                time_str = match.group(2)
                sender = match.group(3).strip()
                content = match.group(4).strip()
                
                # Check for media attachment
                media_match = re.search(r'<([^:]+):\s*([^>]+)>', content)
                media_file = None
                media_type = None
                
                if media_match:
                    media_file = media_match.group(2).strip()
                    if media_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        media_type = 'image'
                    elif media_file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                        media_type = 'video'
                    else:
                        media_type = 'file'
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
                if re.match(r'^[‎\[]?\d{1,2}[\.\/]', line):
                    messages.append(current)
                    current = None
                else:
                    if current['text']:
                        current['text'] += '\n' + line
                    else:
                        current['text'] = line
    
    if current:
        messages.append(current)
    
    # Combine media + text messages
    combined_messages = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        
        if msg['media_file'] and (not msg['text'] or not msg['text'].strip()):
            if i + 1 < len(messages):
                next_msg = messages[i + 1]
                if (next_msg['sender'] == msg['sender'] and 
                    next_msg['date'] == msg['date'] and 
                    next_msg['time'] == msg['time'] and
                    not next_msg['media_file'] and 
                    next_msg['text'] and next_msg['text'].strip()):
                    combined_msg = msg.copy()
                    combined_msg['text'] = next_msg['text']
                    combined_messages.append(combined_msg)
                    i += 2
                    continue
        
        combined_messages.append(msg)
        i += 1
    
    return combined_messages

def determine_own_sender(messages, lang='en'):
    """Determine which sender is 'own'"""
    for msg in messages:
        sender = msg['sender']
        content = msg.get('text', '')
        if is_system_message(sender, content, lang):
            continue
        if not sender.startswith('+') and not sender.replace(' ', '').isdigit():
            return sender
    return None

def format_time(time_str):
    """Format time to hh:mm (remove seconds)"""
    # Handle both hh:mm:ss and hh:mm formats
    parts = time_str.split(':')
    if len(parts) >= 2:
        return f"{parts[0]}:{parts[1]}"
    return time_str

def generate_print_html(messages, folder_name, folder_path):
    """Generate print-optimized HTML"""
    
    lang = detect_language_from_content(messages)
    own_sender = determine_own_sender(messages, lang)
    
    if not own_sender:
        for msg in messages:
            if not is_system_message(msg['sender'], msg.get('text', ''), lang):
                own_sender = msg['sender']
                break
    
    # Extract chat title
    chat_title = folder_name.replace('_', ' ').replace('whatsapp chat ', '').title()
    if messages:
        for msg in messages[:5]:
            sender = msg['sender']
            if '😎' in sender:
                chat_title = sender
                break
    
    # Get year range
    years = set()
    for msg in messages:
        dt = parse_date(msg['date'])
        if dt:
            years.add(dt.year)
    year_range = '/'.join(sorted(str(y) for y in years)) if years else ''
    
    # Count valid messages
    valid_message_count = sum(1 for msg in messages 
                             if not is_system_message(msg['sender'], msg.get('text', ''), lang))
    
    # Video placeholder - match original HTML styling (dark background with play icon)
    video_play_icon_base64 = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iNCA0IDI0IDI0Ij48cGF0aCBmaWxsPSIjRkZGIiBkPSJNMjYgOS45M3YxMi4xNDNjMCAuMzEzLS4xNDUuNTMyLS40MzUuNjZhLjc4My43ODMgMCAwIDEtLjI4LjA1NWMtLjIgMC0uMzY3LS4wNy0uNTAyLS4yMTJsLTQuNDk4LTQuNDk4djEuODUzYzAgLjg4Ni0uMzE0IDEuNjQ0LS45NDMgMi4yNzItLjYzLjYzLTEuMzg2Ljk0My0yLjI3Ljk0M0g5LjIxNGEzLjA5NCAzLjA5NCAwIDAgMS0yLjI3LS45NDNBMy4wOTUgMy4wOTUgMCAwIDEgNiAxOS45MzJ2LTcuODU4YzAtLjg4NS4zMTUtMS42NDMuOTQ0LTIuMjdzMS4zODYtLjk0NiAyLjI3LS45NDZoNy44NThjLjg4NSAwIDEuNjQzLjMxNCAyLjI3Ljk0My42My42My45NDQgMS4zODcuOTQ0IDIuMjcydjEuODRsNC40OTgtNC40ODZjLjEzNC0uMTQuMy0uMjEyLjUwMy0uMjEyLjA5IDAgLjE4Mi4wMi4yOC4wNTYuMjg4LjEyOC40MzMuMzQ3LjQzMy42NnoiLz48L3N2Zz4='
    
    # Generate conversation HTML
    conversation_html = []
    last_date = None
    
    for msg in messages:
        if is_system_message(msg['sender'], msg.get('text', ''), lang):
            continue
        
        # Skip empty messages (reactions without content)
        has_text = msg['text'] and msg['text'].strip()
        has_media = msg['media_file'] is not None
        if not has_text and not has_media:
            continue
        
        # Date separator
        date_formatted = format_date(msg['date'], lang)
        if date_formatted != last_date:
            last_date = date_formatted
            # Add spacer before date separator
            conversation_html.append(f'<div style="height: 0.075in;"></div>')
            conversation_html.append(f'<div style="text-align: center; width: 100%;"><div class="date-separator">{escape(date_formatted)}</div></div>')
        
        # Determine if own or other
        is_own = msg['sender'] == own_sender
        msg_class = 'message-right' if is_own else 'message-left'
        
        # has_text and has_media already defined at loop start for filtering
        
        # Add spacer before message bubble
        conversation_html.append(f'<div style="height: 0.075in;"></div>')
        
        # Start message bubble
        conversation_html.append(f'<div class="message-bubble {msg_class}">')
        
        # Sender name
        conversation_html.append(f'<div class="sender-name">{escape(msg["sender"])}</div>')
        
        # Media handling
        if has_media:
            media_path = folder_path / msg['media_file']
            
            if msg['media_type'] == 'image' and media_path.exists():
                # Use relative path for images - match original HTML structure
                conversation_html.append(f'<div class="message-image">')
                conversation_html.append(f'<img src="{folder_path.name}/{msg["media_file"]}" alt="Image">')
                # Timestamp overlay on image (only if no text)
                if not has_text:
                    conversation_html.append(f'<span class="media-timestamp">{format_time(msg["time"])}</span>')
                conversation_html.append(f'</div>')
            elif msg['media_type'] == 'video':
                # Match original HTML video structure with play icon overlay
                conversation_html.append(f'<div class="message-video">')
                conversation_html.append(f'<div class="video-play-overlay"></div>')
                # Timestamp overlay on video (only if no text)
                if not has_text:
                    conversation_html.append(f'<span class="media-timestamp">{format_time(msg["time"])}</span>')
                conversation_html.append(f'</div>')
            else:
                conversation_html.append(f'<div class="message-file">')
                conversation_html.append(f'<p>📎 {escape(msg["media_file"])}</p>')
                conversation_html.append(f'</div>')
        
        # Text content
        if has_text:
            text = escape(msg['text']).replace('\n', '<br>')
            conversation_html.append(f'<div class="message-text">{text}</div>')
        
        # Timestamp - only show as separate element if there's text
        # For media-only messages, timestamp is overlaid on the media
        if has_text or not has_media:
            conversation_html.append(f'<div class="message-time">{format_time(msg["time"])}</div>')
        
        # End message bubble
        conversation_html.append(f'</div>')
    
    conversation_html_str = '\n'.join(conversation_html)
    
    # Print-optimized CSS - matching original HTML exactly
    print_css = '''
        @page {
            size: Letter;
            margin: 0;
            @bottom-right {
                content: counter(page);
                font-size: 8pt;
                color: #999999;
                margin-right: 0.5in;
                margin-bottom: 0.3in;
            }
        }
        
        @page :first {
            @bottom-right {
                content: none;
            }
        }
        
        @media print {
            body {
                margin: 0;
                padding: 0;
            }
            
            .no-print {
                display: none !important;
            }
            
            @page {
                margin: 0;
            }
            
            /* Hide browser print headers and footers */
            html {
                margin: 0;
            }
            
            /* Ensure proper spacing at top of each page */
            .conversation {
                orphans: 2;
                widows: 2;
            }
            
            /* Add space before elements that start a new page/column */
            .message-bubble,
            .date-separator {
                break-before: avoid-column;
            }
        }
        
        * {
            box-sizing: border-box;
        }
        
        :root {
            --background: #111111;
            --foreground: #1a1a1a;
            --card: #ffffff;
            --muted: #f4f4f5;
            --muted-foreground: #71717a;
            --border: #e4e4e7;
            --chat-outgoing: #0d9488;
            --chat-outgoing-foreground: #ffffff;
            --chat-incoming: #f8f8f8;
            --chat-incoming-foreground: #1a1a1a;
            --primary: #0d9488;
            --radius: 16px;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--background);
            color: var(--foreground);
            padding: 0;
            margin: 0;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            font-size: 9pt;
        }
        
        .print-instructions {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 20px;
            text-align: center;
        }
        
        .print-instructions h2 {
            margin: 0 0 10px 0;
            color: #856404;
            font-size: 18pt;
        }
        
        .print-instructions p {
            margin: 5px 0;
            color: #856404;
            font-size: 11pt;
        }
        
        .content-wrapper {
            background: var(--card);
            min-height: 100vh;
        }
        
        /* Cover Page */
        .cover-page {
            background: white;
            height: 11in;
            width: 8.5in;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            page-break-after: always;
        }
        
        .cover-page h1 {
            font-size: 28pt;
            color: var(--primary);
            margin: 0 0 0.2in 0;
            font-weight: 600;
            text-align: center;
        }
        
        .cover-page .subtitle {
            font-size: 14pt;
            color: var(--muted-foreground);
            margin: 0;
            text-align: center;
        }
        
        .conversation {
            background: var(--background);
            background-image: url("background.jpg");
            background-repeat: repeat-y;
            background-size: 100%;
            padding: 0.4in 0.5in 0.5in 0.5in;
            column-count: 2;
            column-gap: 0.35in;
            column-rule: 1px solid var(--border);
        }
        
        /* Ensure spacing at top of each page/column */
        .conversation > *:first-child {
            margin-top: 0.2in;
        }
        
        .date-separator {
            display: inline-flex;
            align-items: center;
            gap: 0.05in;
            padding: 0.04in 0.12in;
            border-radius: 9999px;
            background: var(--muted);
            font-size: 7pt;
            font-weight: 500;
            color: var(--muted-foreground);
            margin: 0.1in auto 0.1in auto;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            break-after: avoid;
            page-break-after: avoid;
            break-before: avoid-page;
            page-break-before: avoid;
            /* Center in column but keep narrow width */
            width: auto;
        }
        
        .date-separator::before {
            content: "📅";
            font-size: 8pt;
        }
        
        .message-bubble {
            break-inside: avoid;
            page-break-inside: avoid;
            -webkit-column-break-inside: avoid;
            display: block;
            margin-bottom: 0.075in;
            margin-top: 0.075in;
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        
        /* Ensure first message bubble on page has proper top spacing */
        .message-bubble:first-of-type {
            margin-top: 0.25in;
        }
        
        /* Media-only messages should fit content width, not full column width */
        .message-bubble:has(.message-video):not(:has(.message-text)),
        .message-bubble:has(.message-image):not(:has(.message-text)) {
            display: block;
            width: fit-content;
            max-width: 100%;
        }
        
        .message-left {
            background: var(--chat-incoming);
            color: var(--chat-incoming-foreground);
            margin-right: 20%;
        }
        
        .message-right {
            background: var(--chat-outgoing);
            color: var(--chat-outgoing-foreground);
            margin-left: 20%;
        }
        
        .sender-name {
            font-size: 7pt;
            font-weight: 600;
            padding: 0.05in 0.08in 0 0.08in;
            margin: 0;
        }
        
        .message-left .sender-name {
            color: var(--primary);
        }
        
        .message-right .sender-name {
            color: rgba(255, 255, 255, 0.9);
        }
        
        /* Adjust sender name padding for media messages */
        .message-bubble .sender-name {
            padding: 0.05in 0.08in 0.02in 0.08in;
        }
        
        .message-text {
            font-size: 8pt;
            line-height: 1.4;
            padding: 0.05in 0.08in;
            margin: 0;
            word-wrap: break-word;
        }
        
        .message-right .message-text {
            color: var(--chat-outgoing-foreground);
        }
        
        .message-left .message-text {
            color: var(--chat-incoming-foreground);
        }
        
        .message-time {
            font-size: 6pt;
            text-align: right;
            padding: 0.02in 0.15in 0.05in 0.08in;
            margin: 0;
        }
        
        .message-right .message-time {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .message-left .message-time {
            color: var(--muted-foreground);
        }
        
        /* Image Messages - NO PADDING, match original exactly */
        .message-image {
            padding: 0;
            margin: 0;
            break-inside: avoid;
            page-break-inside: avoid;
            -webkit-column-break-inside: avoid;
            position: relative;
            display: block;
        }
        
        /* Ensure message bubbles with images have better bottom margin and break control */
        .message-bubble:has(.message-image) {
            margin-bottom: 0.3in;
        }
        
        .message-image img {
            display: block;
            width: auto;
            max-width: 100%;
            height: auto;
            max-height: 5.25in;
            border-radius: var(--radius);
            object-fit: contain;
        }
        
        /* Timestamp overlay on images - no background */
        .message-image .media-timestamp {
            position: absolute;
            bottom: 0.05in;
            right: 0.05in;
            color: white;
            font-size: 6pt;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
        }
        
        /* Video Messages - match original HTML structure exactly */
        .message-video {
            position: relative;
            width: 256px;
            height: 192px;
            background: rgba(0, 0, 0, 0.9);
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            margin: 0;
            padding: 0;
            break-inside: avoid;
            page-break-inside: avoid;
            -webkit-column-break-inside: avoid;
        }
        
        /* Ensure message bubbles with videos have better bottom margin and break control */
        .message-bubble:has(.message-video) {
            margin-bottom: 0.3in;
        }
        
        /* Video play button overlay - matching original */
        .video-play-overlay::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 3.5rem;
            height: 3.5rem;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 50%;
            z-index: 1;
        }
        
        .video-play-overlay::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 3.5rem;
            height: 3.5rem;
            background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iNCA0IDI0IDI0Ij48cGF0aCBmaWxsPSIjRkZGIiBkPSJNMjYgOS45M3YxMi4xNDNjMCAuMzEzLS4xNDUuNTMyLS40MzUuNjZhLjc4My43ODMgMCAwIDEtLjI4LjA1NWMtLjIgMC0uMzY3LS4wNy0uNTAyLS4yMTJsLTQuNDk4LTQuNDk4djEuODUzYzAgLjg4Ni0uMzE0IDEuNjQ0LS45NDMgMi4yNzItLjYzLjYzLTEuMzg2Ljk0My0yLjI3Ljk0M0g5LjIxNGEzLjA5NCAzLjA5NCAwIDAgMS0yLjI3LS45NDNBMy4wOTUgMy4wOTUgMCAwIDEgNiAxOS45MzJ2LTcuODU4YzAtLjg4NS4zMTUtMS42NDMuOTQ0LTIuMjdzMS4zODYtLjk0NiAyLjI3LS45NDZoNy44NThjLjg4NSAwIDEuNjQzLjMxNCAyLjI3Ljk0My42My42My45NDQgMS4zODcuOTQ0IDIuMjcydjEuODRsNC40OTgtNC40ODZjLjEzNC0uMTQuMy0uMjEyLjUwMy0uMjEyLjA5IDAgLjE4Mi4wMi4yOC4wNTYuMjg4LjEyOC40MzMuMzQ3LjQzMy42NnoiLz48L3N2Zz4=') no-repeat center center;
            background-size: 24px 24px;
            opacity: 0.9;
            z-index: 2;
        }
        
        /* Timestamp overlay on videos - no background */
        .message-video .media-timestamp {
            position: absolute;
            bottom: 0.05in;
            right: 0.05in;
            color: white;
            font-size: 6pt;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
        }
        
        /* File Messages */
        .message-file {
            padding: 0.05in 0.08in;
            margin: 0;
        }
        
        .message-file p {
            font-size: 8pt;
            margin: 0;
            padding-left: 0.15in;
            position: relative;
        }
        
        .message-file p::before {
            content: "📎";
            position: absolute;
            left: 0;
            font-size: 9pt;
            opacity: 0.5;
        }
    '''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{escape(chat_title)} - Print to PDF</title>
<style>
{print_css}
</style>
</head>
<body>
    <div class="print-instructions no-print">
        <h2>📄 Ready to Print!</h2>
        <p><strong>Press Ctrl+P (Windows/Linux) or Cmd+P (Mac)</strong></p>
        <p>Choose "Save as PDF" → Set paper size to <strong>Letter</strong> → Enable <strong>"Background graphics"</strong> → Save</p>
    </div>
    
    <div class="content-wrapper">
        <div class="cover-page">
            <h1>{escape(chat_title)}</h1>
        </div>
        
        <div class="conversation">
{conversation_html_str}
        </div>
    </div>
</body>
</html>'''
    
    return html

def main():
    print("=" * 60)
    print("   WhatsApp-To-PDF (Print-Ready HTML)")
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
    
    print("🔄 Processing chat...")
    
    try:
        # Parse messages
        messages = parse_chat_file(chat_file)
        print(f"✅ {len(messages)} messages parsed")
        
        if len(messages) == 0:
            print("❌ No messages found!")
            return
        
        # Generate HTML
        print("📝 Creating print-ready HTML...")
        folder_name = folder_path.name
        html = generate_print_html(messages, folder_name, folder_path)
        
        # Save HTML file
        html_output_path = folder_path.parent / f"{folder_name}_print.html"
        html_output_path.write_text(html, encoding='utf-8')
        
        print()
        print("=" * 60)
        print(f"✅ DONE!")
        print(f"📄 HTML saved: {html_output_path}")
        print(f"💾 Size: {html_output_path.stat().st_size / 1024:.1f} KB")
        print()
        print("📖 Next steps:")
        print("   1. Opening the HTML file in your browser...")
        print("   2. Press Ctrl+P (or Cmd+P on Mac)")
        print("   3. Choose 'Save as PDF'")
        print("   4. Set paper size: Letter")
        print("   5. Enable 'Background graphics'")
        print("   6. Save your PDF!")
        print()
        print("=" * 60)
        
        # Try to open in browser
        try:
            webbrowser.open(str(html_output_path.absolute()))
            print("🌐 Browser opened automatically!")
        except:
            print(f"💡 Please open this file manually: {html_output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
