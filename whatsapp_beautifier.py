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
    
    return messages

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
    """Generate HTML matching CopyTrans structure"""
    
    # Determine own sender
    own_sender = determine_own_sender(messages)
    if not own_sender:
        # Fallback: use first non-system sender
        for msg in messages:
            if not any(x in msg['sender'] for x in ['😎', 'WhatsApp', 'erstellt', 'hinzugefügt', 'geändert']):
                own_sender = msg['sender']
                break
    
    # Extract chat title from folder name or first message
    chat_title = folder_name.replace('_', ' ').replace('whatsapp chat ', '').title()
    if messages:
        first_sender = messages[0]['sender']
        if '😎' in first_sender:
            # Extract emoji and name
            parts = first_sender.split(' ')
            if len(parts) > 1:
                chat_title = ' '.join(parts[1:]) if len(parts) > 1 else first_sender
    
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
                conversation_html.append(f'        <li class="clear"></li>')
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
        
        # Start new message group if sender changed or if no group is open
        if not current_group_open or msg['sender'] != last_sender or is_own != last_is_own:
            # Close previous group if exists
            if current_group_open:
                conversation_html.append(f'            </ol>')
                conversation_html.append(f'        </li>')
                conversation_html.append(f'        <li class="clear"></li>')
            
            # Start new message group
            conversation_html.append(f'        <li class="{msg_class}">')
            conversation_html.append(f'            <ol class="messages">')
            current_group_open = True
            
            # User picture (placeholder)
            conversation_html.append(f'                <li class="user-picture">')
            conversation_html.append(f'                    <img src="no-user.jpg" alt="{escape(msg["sender"])}">')
            conversation_html.append(f'                </li>')
            
            # User name (only for others)
            if not is_own:
                conversation_html.append(f'                <li class="user-name">')
                conversation_html.append(f'                    <p>{escape(msg["sender"])}</p>')
                conversation_html.append(f'                </li>')
            else:
                conversation_html.append(f'                <li class="user-name">')
                conversation_html.append(f'                    <p></p>')
                conversation_html.append(f'                </li>')
        
        # Message content
        has_text = msg['text'] and msg['text'].strip()
        has_media = msg['media_file'] is not None
        
        if has_media:
            media_path = f'{folder_name}/{msg["media_file"]}'
            if msg['media_type'] == 'image':
                conversation_html.append(f'                <li class="message image">')
                conversation_html.append(f'                    <a class="shared" href="{media_path}">')
                conversation_html.append(f'                        <img class="img-shared" src="{media_path}">')
                conversation_html.append(f'                        <span class="zoom"></span>')
                conversation_html.append(f'                    </a>')
                conversation_html.append(f'                    <span class="hours">{msg["time"]}</span>')
                conversation_html.append(f'                </li>')
            elif msg['media_type'] == 'video':
                conversation_html.append(f'                <li class="message video">')
                conversation_html.append(f'                    <a class="shared" href="{media_path}">')
                conversation_html.append(f'                        <p>{escape(msg["media_file"])}</p>')
                conversation_html.append(f'                    </a>')
                conversation_html.append(f'                    <span class="hours">{msg["time"]}</span>')
                conversation_html.append(f'                </li>')
            else:
                conversation_html.append(f'                <li class="message file">')
                conversation_html.append(f'                    <p>{escape(msg["media_file"])}</p>')
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
        conversation_html.append(f'        <li class="clear"></li>')
    
    conversation_html_str = '\n'.join(conversation_html)
    
    # Load CSS template from copyTrans
    css_template_path = Path(__file__).parent / 'style.css'
    if css_template_path.exists():
        css_template = css_template_path.read_text(encoding='utf-8')
        # Add border-radius to videos if not present
        if 'ol.conversation li ol.messages li.video' in css_template and 'border-radius' not in css_template.split('ol.conversation li ol.messages li.video')[1].split('}')[0]:
            # Insert border-radius after background in video CSS
            css_template = css_template.replace(
                '    ol.conversation li ol.messages li.video,\n    ol.conversation li.left ol.messages li.video,\n    ol.conversation li.right ol.messages li.video\n    {\n        position: relative;\n        width: 250px;\n        height: 150px;\n        background: rgba(0,0,0,0.8);\n    }',
                '    ol.conversation li ol.messages li.video,\n    ol.conversation li.left ol.messages li.video,\n    ol.conversation li.right ol.messages li.video\n    {\n        position: relative;\n        width: 250px;\n        height: 150px;\n        background: rgba(0,0,0,0.8);\n        border-radius: 20px;\n        -webkit-border-radius: 20px;\n    }'
            )
    else:
        # Fallback: use inline CSS (simplified version)
        print("⚠️  Warning: style.css not found, using inline CSS")
        css_template = None
    
    if not css_template:
        raise FileNotFoundError("style.css not found! Please extract it from copy_trans_version.html first.")
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Unterhaltung mit {escape(chat_title)}</title>
<style type="text/css">
{css_template}
</style>
</head>
<body>
<a id="top">&nbsp;</a>
<div id="wrapper">

    <header class="title">
        <div class="content">
            <h1>Unterhaltung mit {escape(chat_title)}</h1>
            <a class="nav-button" href="#bottom">
                <span>↓</span>
            </a>
            <a class="nav-button" href="#top">
                <span>↑</span>
            </a>
        </div>
    </header>
    <ol class="conversation">

{conversation_html_str}

    </ol>
    <a id="bottom">&nbsp;</a>
</div>
</body>
</html>'''
    
    return html

def main():
    print("=" * 60)
    print("   WhatsApp Chat Beautifier - CopyTrans Style")
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
