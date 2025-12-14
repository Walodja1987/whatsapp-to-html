#!/usr/bin/env python3
"""
Update _chat.txt file to replace .mov with .mp4 in media file references
This script updates the chat file after converting .mov files to .mp4 format
"""

import sys
import re
import shutil
from pathlib import Path
from datetime import datetime

def update_chat_file(chat_path, backup=True):
    """
    Update _chat.txt file to replace .mov with .mp4 in media references
    
    Args:
        chat_path: Path to the _chat.txt file
        backup: Whether to create a backup of the original file
    
    Returns:
        Tuple of (success: bool, replacements_count: int)
    """
    chat_path = Path(chat_path)
    
    if not chat_path.exists():
        print(f"❌ File not found: {chat_path}")
        return False, 0
    
    if not chat_path.name == '_chat.txt':
        print(f"⚠️  Warning: Expected _chat.txt, but found: {chat_path.name}")
        # Continue anyway, user might have renamed it
    
    # Create backup if requested
    if backup:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = chat_path.parent / f'_chat.txt.backup_{timestamp}'
        try:
            shutil.copy2(chat_path, backup_path)
            print(f"📋 Created backup: {backup_path.name}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
            # Continue anyway - backup is optional
    
    # Read the file
    try:
        with open(chat_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False, 0
    
    # Count replacements before making changes
    # Pattern matches: <WORD: filename.mov> or <WORD: filename.MOV>
    # where WORD can be any language (Anhang, Attachment, Anexo, etc.)
    mov_pattern = r'(<[^:]+:\s*)([^>]+\.mov)(>)'
    mov_pattern_case_insensitive = re.compile(mov_pattern, re.IGNORECASE)
    
    matches = list(mov_pattern_case_insensitive.finditer(content))
    replacement_count = len(matches)
    
    if replacement_count == 0:
        print(f"ℹ️  No .mov references found in {chat_path.name}")
        return True, 0
    
    # Perform replacements
    # Replace .mov and .MOV with .mp4 (case-insensitive)
    def replace_mov(match):
        prefix = match.group(1)  # <WORD: 
        filename = match.group(2)  # filename.mov
        suffix = match.group(3)    # >
        # Replace .mov/.MOV with .mp4
        new_filename = re.sub(r'\.mov$', '.mp4', filename, flags=re.IGNORECASE)
        return prefix + new_filename + suffix
    
    updated_content = mov_pattern_case_insensitive.sub(replace_mov, content)
    
    # Write the updated content
    try:
        with open(chat_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ Updated {chat_path.name}: {replacement_count} .mov reference(s) replaced with .mp4")
        return True, replacement_count
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False, 0

def update_directory(directory_path, backup=True):
    """
    Update _chat.txt file in a directory
    
    Args:
        directory_path: Path to directory containing _chat.txt
        backup: Whether to create a backup of the original file
    """
    directory_path = Path(directory_path)
    
    if not directory_path.exists() or not directory_path.is_dir():
        print(f"❌ Directory not found: {directory_path}")
        return
    
    chat_file = directory_path / '_chat.txt'
    
    if not chat_file.exists():
        print(f"❌ _chat.txt not found in: {directory_path}")
        return
    
    success, count = update_chat_file(chat_file, backup=backup)
    
    if success:
        print()
        print("=" * 60)
        print(f"✅ Update complete!")
        print(f"   Replacements: {count}")
        print("=" * 60)

def main():
    print("=" * 60)
    print("   Update _chat.txt - Replace .mov with .mp4")
    print("=" * 60)
    print()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 update_chat_txt.py <chat_file_or_directory> [--no-backup]")
        print()
        print("Options:")
        print("  --no-backup    Don't create a backup of _chat.txt before updating")
        print()
        print("Examples:")
        print("  python3 update_chat_txt.py my_whatsapp_data/")
        print("  python3 update_chat_txt.py my_whatsapp_data/_chat.txt")
        print("  python3 update_chat_txt.py my_whatsapp_data/ --no-backup")
        return
    
    input_path = Path(sys.argv[1])
    backup = '--no-backup' not in sys.argv
    
    if input_path.is_file():
        # Update single file
        success, count = update_chat_file(input_path, backup=backup)
        if success:
            print()
            print("=" * 60)
            print(f"✅ Update complete!")
            print(f"   Replacements: {count}")
            print("=" * 60)
    elif input_path.is_dir():
        # Update _chat.txt in directory
        update_directory(input_path, backup=backup)
    else:
        print(f"❌ Path not found: {input_path}")

if __name__ == '__main__':
    main()
