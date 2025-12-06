# WhatsApp Chat Beautifier

A Python tool that converts exported WhatsApp chat files into beautifully formatted HTML files locally. Perfect for archiving, viewing, or sharing your WhatsApp conversations with a beautiful interface.

## Requirements

- Python 3.6 or higher
- A WhatsApp chat export (with or without media)

## Installation

1. Clone or download this repository. The directory structure should look like this:
```
whatsapp-beautifier/
├── whatsapp_beautifier.py
├── style.css
├── background.jpg
├── no-user.jpg
├── README.md
```
3. Ensure you have Python 3 installed on your system
4. No additional Python packages are required (uses only standard library)

## Usage

### Step 1: Export WhatsApp Chat

1. Open WhatsApp on your phone
2. Select the chat you want to export
3. Tap on the chat name at the top
4. **Scroll** to the bottom where you will find **"Export chat"**
5. Click on it and select whether you want to download it with or without media
6. Save the zip file. I recommend using Google Drive or Dropbox, then transfer it to your local machine

### Step 2: Prepare Your Data

1. Extract the zip file
2. Copy the extracted folder to the directory where this code lives
3. Name the folder as you want (e.g., `my_whatsapp_data`)

Your directory structure should now look like this:
```
whatsapp-beautifier/
├── whatsapp_beautifier.py
├── style.css
├── background.jpg
├── README.md
├── my_whatsapp_data/ (added)
│   ├── _chat.txt
│   ├── [photos and videos]
│   └── ...
```

### Step 3: Run the Script

Run the Python script with your folder name as an argument:

```bash
python3 whatsapp_beautifier.py my_whatsapp_data
```

Replace `my_whatsapp_data` with the name of your WhatsApp data folder.

### Step 4: View Your Chat

- The script will generate a file called `my_whatsapp_data_chat.html` in the same directory
- Double-click the HTML file to open it in your web browser
- **Important:** The HTML output file must be in the same directory as your WhatsApp data folder for images and media to load correctly. This is especially important if you want to move the files to another folder or an external drive like a USB stick.

## Customization

### Background Image

- You can replace `background.jpg` with your own background image
- The file must be named `background.jpg`
- Place it in the same directory as the script

### User Profile Picture

- You can replace the existing `no-user.jpg` (or `no_user.jpg`) file with your own profile picture
- It will be used as the default profile picture for all users in the chat

## File Structure

After running the script, your directory structure should look like this:

```
whatsapp-beautifier/
├── whatsapp_beautifier.py
├── style.css
├── background.jpg
├── README.md
├── my_whatsapp_data/
│   ├── _chat.txt
│   ├── [photos and videos]
│   └── ...
└── my_whatsapp_data_chat.html (generated)
```

## Troubleshooting

- **Images not loading?** Make sure the HTML file and the WhatsApp data folder are in the same directory
- **Script can't find `_chat.txt`?** Ensure you've extracted the WhatsApp export zip and the folder contains the `_chat.txt` file
- **Missing background?** The script will work without `background.jpg`, but you may want to add one for a better visual experience

## Notes

- The script automatically detects which messages are yours vs. other participants
- System messages (like "group created", "member added", etc.) are automatically filtered out
- Media files (images, videos) are displayed inline when available
- The output HTML is self-contained but references media files from the data folder
