# WhatsApp-To-HTML

A Python tool that converts exported WhatsApp chat files into beautifully formatted HTML files locally. Perfect for archiving, viewing, or sharing your WhatsApp conversations with a beautiful interface.

<img width="800" height="876" alt="image" src="https://github.com/user-attachments/assets/080e8b49-998d-4d90-82fb-1a5af338135f" />

## How to run (quick commands during development)

```bash
# Complete conversion with recommended options
python3 generate_html.py my_whatsapp_data --delete-original
```

```bash
# Rerun HTML generation (e.g., if `scripts/convert_whatsapp_to_html.py` script changes)
python3 scripts/convert_whatsapp_to_html.py my_whatsapp_data
```


## Requirements

- A WhatsApp chat export (see instructions below)
- Python 3.6 or higher (no additional Python packages are required as it uses only standard library)
- **ffmpeg** (required if your chat contains .mov video files) - See installation instructions below

## Installation

Clone this repository to your local machine. The directory structure should look like this:
```
whatsapp-to-html/
├── generate_html.py         # Main entry point
├── scripts/
│   ├── convert_whatsapp_to_html.py
│   ├── convert_mov_to_mp4.py
│   └── update_chat_txt.py
├── style.css
├── background.jpg
├── README.md
├── CONTRIBUTING.md
├── .gitignore
```


## Usage

### Step 1: Export WhatsApp Chat

**On iOS:**
* **Open WhatsApp** on your phone
* **Select the chat** you want to export
* Tap on the chat **name at the top**
* **Scroll to the bottom** where you will find **"Export chat"**
* Click on it and select whether you want to download it *with* or *without* media
* Slide the second line to the right, click on "More" (three dots icon), and choose where to save the zip file. It is recommended to choose Google Drive or Dropbox and then download it to your local machine afterwards, or email it to yourself.

**On Android:**
* **Open WhatsApp** on your phone
* **Select the chat** you want to export
* Tap the **three dots menu** (⋮) in the top right corner
* Select **"More"** from the menu
* Tap **"Export chat"**
* Choose whether you want to export **with media** or **without media**
* Select where to save the zip file (recommended: Google Drive, Dropbox, or email it to yourself)
* Download the zip file to your local machine

### Step 2: Prepare Your Data

* Extract the zip file on your local machine
* Place the extracted folder within the cloned repository (where the `generate_html.py` file resides).
* Give the extracted folder any name you prefer (for example, `my_whatsapp_data`). The generated HTML file will use this folder name as a prefix (e.g., `my_whatsapp_data_chat.html`). To prevent issues during processing, avoid using special characters such as ä, ö, ü, etc..

Your directory structure should now look like this:
```
whatsapp-to-html/
├── generate_html.py
├── scripts/
│   └── ...
├── style.css
├── background.jpg
├── README.md
├── CONTRIBUTING.md
├── .gitignore
├── my_whatsapp_data/ (added)
│   ├── _chat.txt
│   ├── [photos and videos]
│   └── ...
```

### Step 3: Convert to HTML

The easiest way to convert your WhatsApp chat is using the main script `generate_html.py`, which automatically runs all necessary steps in the correct order:

1. **Converts .mov files to .mp4** (if your chat contains QuickTime videos)
2. **Updates _chat.txt** to replace .mov references with .mp4
3. **Generates the HTML file** from your chat

**Install ffmpeg** (if not already installed and your chat contains .mov files):
- **Windows**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Linux (Ubuntu/Debian)**: `sudo apt-get install ffmpeg`
- **Linux (CentOS/RHEL)**: `sudo yum install ffmpeg`

**Run the main script:**

```bash
python3 generate_html.py my_whatsapp_data --delete-original
```

**Options:**
- `--recursive, -r` - Search subdirectories recursively for .mov files
- `--overwrite, -f` - Overwrite existing .mp4 files
- `--delete-original` - Delete original .mov files after conversion (recommended to save disk space)
- `--no-backup` - Don't create backup of _chat.txt before updating
- `--skip-mov-convert` - Skip .mov to .mp4 conversion step
- `--skip-update-chat` - Skip _chat.txt update step

**Examples:**
```bash
# Complete conversion with recommended options
python3 generate_html.py my_whatsapp_data --delete-original

# Recursive conversion for nested folders
python3 generate_html.py my_whatsapp_data --recursive --delete-original

# Skip video conversion if already done
python3 generate_html.py my_whatsapp_data --skip-mov-convert
```

**Note:** It is recommended to use the `--delete-original` flag to save disk space, as you won't need the original .mov files anymore.

After running the script, your directory structure should look like this:

```
whatsapp-to-html/
├── generate_html.py
├── scripts/
│   ├── convert_whatsapp_to_html.py
│   ├── convert_mov_to_mp4.py
│   └── update_chat_txt.py
├── style.css
├── background.jpg
├── README.md
├── CONTRIBUTING.md
├── .gitignore
├── my_whatsapp_data/
│   ├── _chat.txt
│   ├── [photos and videos]
│   └── ...
└── my_whatsapp_data_chat.html (generated)
```

### Step 4: View Your Chat

- The script will generate a file called `my_whatsapp_data_chat.html` in the same directory
- Double-click the HTML file to open it in your web browser

## Moving Files to a Different Location

If you want to move the files to another folder or drive (external storage or USB), you have to move the following files to ensure that the HTML will load and display images and media correctly:
   - Your WhatsApp data folder (e.g., `my_whatsapp_data`)
   - The HTML output file (e.g., `my_whatsapp_data_chat.html`)
   - `background.jpg`
   - `style.css`


## Customization

You can replace `background.jpg` with your own background image. The file must be named `background.jpg`. You don't have to rerun the HTML generation.

You can find free background images on [freepik.com](https://www.freepik.com/free-photos-vectors/simple-doodle-background/3#uuid=8c9be20a-6071-4b39-ac3a-94efe1277c55).


## Language Support

The tool automatically detects the language of your WhatsApp export and adapts accordingly:

- **Supported languages**: German, English, Spanish, French, Italian
- **Date formats**: Supports both European (DD.MM.YY) and US (MM/DD/YY) date formats
- **Auto-detection**: The language is automatically detected from your chat content
- **Month names**: Displayed in the detected language (e.g., "January" in English, "Januar" in German)

**Note**: The current version has been tested using German WhatsApp exports only. While the tool is designed to support multiple languages, other languages may need additional testing and refinement.





## Advanced Usage: Individual Scripts

For more fine-grained control, you can run each script separately:

### Step 1: Convert .mov Files to .mp4

If your WhatsApp chat contains QuickTime (.mov) video files, convert them to .mp4 format for better browser compatibility:

```bash
python3 scripts/convert_mov_to_mp4.py my_whatsapp_data --delete-original
```

**Options:**
- `--recursive, -r` - Search subdirectories recursively
- `--overwrite, -f` - Overwrite existing .mp4 files
- `--delete-original` - Delete original .mov files after successful conversion

### Step 2: Update _chat.txt

Update the chat file to replace .mov references with .mp4:

```bash
python3 scripts/update_chat_txt.py my_whatsapp_data/
```

**Options:**
- `--no-backup` - Don't create a backup of _chat.txt before updating

**Note:** A timestamped backup of `_chat.txt` is created automatically (e.g., `_chat.txt.backup_20241225_143022`) in the same directory.

### Step 3: Generate HTML

Convert the chat to HTML:

```bash
python3 scripts/convert_whatsapp_to_html.py my_whatsapp_data
```


