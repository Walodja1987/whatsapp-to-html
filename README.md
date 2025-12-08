# WhatsApp-To-HTML

A Python tool that converts exported WhatsApp chat files into beautifully formatted HTML files locally. Perfect for archiving, viewing, or sharing your WhatsApp conversations with a beautiful interface.

<img width="800" height="876" alt="image" src="https://github.com/user-attachments/assets/080e8b49-998d-4d90-82fb-1a5af338135f" />

## Requirements

- A WhatsApp chat export (see instructions below)
- Python 3.6 or higher (no additional Python packages are required for HTML conversion)
- **For PDF conversion**: WeasyPrint library (`pip install weasyprint`)

## Installation

Clone this repository to your local machine. The directory structure should look like this:
```
whatsapp-to-html/
├── convert_whatsapp_to_html.py
├── convert_whatsapp_to_pdf.py
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
* Click on it and select whether you want to download it with or without media
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
* Place the extracted folder within the cloned repository (where the `convert_whatsapp_to_html.py` file resides).
* Name the extracted folder to whatever you like (e.g., `my_whatsapp_data`). Avoid using special characters like ä, ö, ü, etc., to prevent issues during processing.

Your directory structure should now look like this:
```
whatsapp-to-html/
├── convert_whatsapp_to_html.py
├── convert_whatsapp_to_pdf.py
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

### Step 3: Run the Script

Run the Python script with your folder name as an argument (ensure you have Python 3 installed on your system):

```bash
python3 convert_whatsapp_to_html.py my_whatsapp_data
```

Replace `my_whatsapp_data` with the name of your WhatsApp data folder.

### Step 4: View Your Chat

- The script will generate a file called `my_whatsapp_data_chat.html` in the same directory
- Double-click the HTML file to open it in your web browser
- **Important:** **The HTML output file, the `background.jpg` and `styles.css` files must be in the same directory as your WhatsApp data folder for images and media to load and display correctly.** This is especially important if you want to move the files to another folder or an external drive like a USB stick.

## PDF Conversion for Printing

You can also convert your WhatsApp chat to a printable PDF format with a two-column layout, similar to printed chat books.

### Requirements

First, install WeasyPrint:

```bash
pip install weasyprint
```

**Note:** WeasyPrint may require additional system dependencies depending on your operating system. See the [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) if you encounter issues.

### Usage

Run the PDF conversion script:

```bash
python3 convert_whatsapp_to_pdf.py my_whatsapp_data
```

This will generate:
- `my_whatsapp_data_chat.pdf` - The printable PDF file
- `my_whatsapp_data_print.html` - A preview HTML file (for debugging)

### PDF Features

- **Two-column layout** optimized for Letter-size paper (8.5" × 11")
- **Embedded images** with automatic sizing:
  - Portrait images: 2 fit per page (max 3.5" height)
  - Landscape images: 4 fit per page (max 1.8" height)
- **Video placeholders** with play icon and filename
- **Smart page breaks** to keep messages together
- **Page numbers** in the footer
- **Chronological flow** across columns

### Tips for Printing

- Print double-sided for a book-like format
- Use a duplex printer or manually flip pages
- Consider binding options: spiral binding, staples, or folder
- For long chats, print in sections or date ranges

## Language Support

The tool automatically detects the language of your WhatsApp export and adapts accordingly:

- **Supported languages**: German, English, Spanish, French, Italian
- **Date formats**: Supports both European (DD.MM.YY) and US (MM/DD/YY) date formats
- **Auto-detection**: The language is automatically detected from your chat content
- **Month names**: Displayed in the detected language (e.g., "January" in English, "Januar" in German)

**Note**: The current version has been tested using German WhatsApp exports only. While the tool is designed to support multiple languages, other languages may need additional testing and refinement.

## Customization

### Background Image

- You can replace `background.jpg` with your own background image
- The file must be named `background.jpg`
- You can find free background images on [freepik.com](https://www.freepik.com/free-photos-vectors/simple-doodle-background/3#uuid=8c9be20a-6071-4b39-ac3a-94efe1277c55)

## File Structure

After running the script, your directory structure should look like this:

```
whatsapp-to-html/
├── convert_whatsapp_to_html.py
├── convert_whatsapp_to_pdf.py
├── style.css
├── background.jpg
├── README.md
├── CONTRIBUTING.md
├── .gitignore
├── my_whatsapp_data/
│   ├── _chat.txt
│   ├── [photos and videos]
│   └── ...
├── my_whatsapp_data_chat.html (generated by HTML script)
├── my_whatsapp_data_chat.pdf (generated by PDF script)
└── my_whatsapp_data_print.html (generated by PDF script)
```
