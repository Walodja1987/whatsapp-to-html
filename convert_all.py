#!/usr/bin/env python3
"""
Master script that runs all conversion steps in order:
1. Convert .mov files to .mp4
2. Update _chat.txt to replace .mov with .mp4 references
3. Generate HTML from the chat
"""

import sys
import subprocess
from pathlib import Path

def run_command(script_name, args, description):
    """
    Run a Python script and return success status
    
    Args:
        script_name: Name of the script to run
        args: List of arguments to pass to the script
        description: Description of what the script does
    
    Returns:
        True if successful, False otherwise
    """
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        return False
    
    print()
    print("=" * 60)
    print(f"   {description}")
    print("=" * 60)
    print()
    
    cmd = [sys.executable, str(script_path)] + args
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
        return False

def main():
    print("=" * 60)
    print("   WhatsApp Chat - Complete Conversion Pipeline")
    print("=" * 60)
    print()
    print("This script will run all conversion steps in order:")
    print("  1. Convert .mov files to .mp4")
    print("  2. Update _chat.txt to replace .mov with .mp4 references")
    print("  3. Generate HTML from the chat")
    print()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 convert_all.py <whatsapp_folder> [options]")
        print()
        print("Options (passed to conversion script):")
        print("  --recursive, -r       Search subdirectories recursively for .mov files")
        print("  --overwrite, -f       Overwrite existing .mp4 files")
        print("  --delete-original     Delete original .mov files after conversion")
        print("  --no-backup           Don't create backup of _chat.txt")
        print("  --skip-mov-convert    Skip .mov to .mp4 conversion step")
        print("  --skip-update-chat    Skip _chat.txt update step")
        print()
        print("Examples:")
        print("  python3 convert_all.py my_whatsapp_data")
        print("  python3 convert_all.py my_whatsapp_data --delete-original")
        print("  python3 convert_all.py my_whatsapp_data --recursive --delete-original")
        return
    
    folder_path = Path(sys.argv[1])
    
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return
    
    if not folder_path.is_dir():
        print(f"❌ Not a directory: {folder_path}")
        return
    
    # Check for _chat.txt
    chat_file = folder_path / '_chat.txt'
    if not chat_file.exists():
        print(f"❌ _chat.txt not found in: {folder_path}")
        return
    
    # Extract options
    all_args = sys.argv[2:]
    skip_mov_convert = '--skip-mov-convert' in all_args
    skip_update_chat = '--skip-update-chat' in all_args
    no_backup = '--no-backup' in all_args
    
    # Filter out our special options
    conversion_args = [arg for arg in all_args 
                     if arg not in ['--skip-mov-convert', '--skip-update-chat', '--no-backup']]
    
    # Add folder path to conversion args
    conversion_args = [str(folder_path)] + conversion_args
    
    # Step 1: Convert .mov to .mp4
    if not skip_mov_convert:
        print(f"📁 Processing folder: {folder_path.name}")
        success = run_command(
            'convert_mov_to_mp4.py',
            conversion_args,
            'Step 1: Convert .mov Files to .mp4'
        )
        if not success:
            print()
            print("❌ Step 1 failed. Aborting.")
            return
    else:
        print()
        print("⏭️  Skipping .mov to .mp4 conversion (--skip-mov-convert)")
    
    # Step 2: Update _chat.txt
    if not skip_update_chat:
        update_args = [str(folder_path)]
        if no_backup:
            update_args.append('--no-backup')
        
        success = run_command(
            'update_chat_txt.py',
            update_args,
            'Step 2: Update _chat.txt'
        )
        if not success:
            print()
            print("❌ Step 2 failed. Aborting.")
            return
    else:
        print()
        print("⏭️  Skipping _chat.txt update (--skip-update-chat)")
    
    # Step 3: Generate HTML
    html_args = [str(folder_path)]
    success = run_command(
        'convert_whatsapp_to_html.py',
        html_args,
        'Step 3: Generate HTML'
    )
    
    if success:
        print()
        print("=" * 60)
        print("✅ ALL STEPS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print(f"📄 HTML file generated: {folder_path.name}_chat.html")
        print(f"📁 Location: {folder_path.parent}")
    else:
        print()
        print("❌ Step 3 failed.")
        return

if __name__ == '__main__':
    main()
