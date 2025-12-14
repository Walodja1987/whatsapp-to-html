#!/usr/bin/env python3
"""
Convert .mov files to .mp4 format
Uses ffmpeg to convert QuickTime .mov files to MP4 format for better browser compatibility
"""

import sys
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_mov_to_mp4(input_path, output_path=None, overwrite=False, delete_original=False):
    """
    Convert a .mov file to .mp4 using ffmpeg
    
    Args:
        input_path: Path to the .mov file
        output_path: Optional output path (default: same as input but with .mp4 extension)
        overwrite: Whether to overwrite existing .mp4 files
        delete_original: Whether to delete the original .mov file after successful conversion
    
    Returns:
        True if conversion successful, False otherwise
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        return False
    
    if not input_path.suffix.lower() == '.mov':
        print(f"⚠️  Warning: {input_path} is not a .mov file")
        return False
    
    if output_path is None:
        output_path = input_path.with_suffix('.mp4')
    else:
        output_path = Path(output_path)
    
    if output_path.exists() and not overwrite:
        print(f"⏭️  Skipping {input_path.name} (output already exists: {output_path.name})")
        return False
    
    print(f"🔄 Converting: {input_path.name} → {output_path.name}")
    
    try:
        # Use ffmpeg to convert with H.264 codec for maximum compatibility
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',  # H.264 video codec
            '-c:a', 'aac',      # AAC audio codec
            '-preset', 'medium', # Encoding speed/quality balance
            '-crf', '23',       # Quality (18-28, lower is better quality)
            '-movflags', '+faststart',  # Enable fast start for web playback
            '-y' if overwrite else '-n',  # Overwrite or don't overwrite
            str(output_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ Successfully converted: {output_path.name}")
        
        # Delete original file if requested
        if delete_original:
            try:
                input_path.unlink()
                print(f"🗑️  Deleted original file: {input_path.name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not delete original file {input_path.name}: {e}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {input_path.name}:")
        print(f"   {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def convert_directory(directory_path, recursive=False, overwrite=False, delete_original=False):
    """
    Convert all .mov files in a directory
    
    Args:
        directory_path: Path to directory containing .mov files
        recursive: Whether to search subdirectories
        overwrite: Whether to overwrite existing .mp4 files
        delete_original: Whether to delete the original .mov files after successful conversion
    """
    directory_path = Path(directory_path)
    
    if not directory_path.exists() or not directory_path.is_dir():
        print(f"❌ Directory not found: {directory_path}")
        return
    
    # Find all .mov files
    if recursive:
        mov_files = list(directory_path.rglob('*.mov'))
        mov_files.extend(directory_path.rglob('*.MOV'))
    else:
        mov_files = list(directory_path.glob('*.mov'))
        mov_files.extend(directory_path.glob('*.MOV'))
    
    if not mov_files:
        print(f"ℹ️  No .mov files found in {directory_path}")
        return
    
    print(f"📁 Found {len(mov_files)} .mov file(s)")
    print()
    
    successful = 0
    failed = 0
    skipped = 0
    
    for mov_file in mov_files:
        output_file = mov_file.with_suffix('.mp4')
        if output_file.exists() and not overwrite:
            skipped += 1
            continue
        
        if convert_mov_to_mp4(mov_file, overwrite=overwrite, delete_original=delete_original):
            successful += 1
        else:
            failed += 1
        print()
    
    print("=" * 60)
    print(f"✅ Conversion complete!")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Skipped: {skipped}")
    print("=" * 60)

def main():
    print("=" * 60)
    print("   MOV to MP4 Converter")
    print("=" * 60)
    print()
    
    # Check if ffmpeg is installed
    if not check_ffmpeg():
        print("❌ Error: ffmpeg is not installed or not in PATH")
        print()
        print("Please install ffmpeg:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("  - macOS:   brew install ffmpeg")
        print("  - Linux:   sudo apt-get install ffmpeg  (Ubuntu/Debian)")
        print("             sudo yum install ffmpeg      (CentOS/RHEL)")
        return
    
    print("✅ ffmpeg found")
    print()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 convert_mov_to_mp4.py <file_or_directory> [--recursive] [--overwrite] [--delete-original]")
        print()
        print("Options:")
        print("  --recursive, -r       Search subdirectories recursively")
        print("  --overwrite, -f       Overwrite existing .mp4 files")
        print("  --delete-original     Delete original .mov files after successful conversion")
        print()
        print("Examples:")
        print("  python3 convert_mov_to_mp4.py video.mov")
        print("  python3 convert_mov_to_mp4.py whatsapp_chat_folder/")
        print("  python3 convert_mov_to_mp4.py whatsapp_chat_folder/ --recursive")
        print("  python3 convert_mov_to_mp4.py whatsapp_chat_folder/ --recursive --overwrite")
        print("  python3 convert_mov_to_mp4.py whatsapp_chat_folder/ --delete-original")
        return
    
    input_path = Path(sys.argv[1])
    recursive = '--recursive' in sys.argv or '-r' in sys.argv
    overwrite = '--overwrite' in sys.argv or '-f' in sys.argv
    delete_original = '--delete-original' in sys.argv
    
    if input_path.is_file():
        # Convert single file
        convert_mov_to_mp4(input_path, overwrite=overwrite, delete_original=delete_original)
    elif input_path.is_dir():
        # Convert all .mov files in directory
        convert_directory(input_path, recursive=recursive, overwrite=overwrite, delete_original=delete_original)
    else:
        print(f"❌ Path not found: {input_path}")

if __name__ == '__main__':
    main()
