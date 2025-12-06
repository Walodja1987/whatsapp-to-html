# WhatsApp Chat Beautifier

A Python tool that converts exported WhatsApp chat files into beautifully formatted HTML files locally. Perfect for archiving, viewing, or sharing your WhatsApp conversations with a beautiful interface.

## Requirements

- A WhatsApp chat export (see instructions below)
- Python 3.6 or higher (no additional Python packages are required as it uses only standard library)

## Installation

Clone this repository to your local machine. The directory structure should look like this:
```
whatsapp-beautifier/
├── whatsapp_beautifier.py
├── style.css
├── background.jpg
├── README.md
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
* Place the extracted folder within the cloned repository (where the `whatsapp_beautifier.py` file resides).
* Name the extracted folder to whatever you like (e.g., `my_whatsapp_data`). Avoid using special characters like ä, ö, ü, etc., to prevent issues during processing.

Your directory structure should now look like this:
```
whatsapp-beautifier/
├── whatsapp_beautifier.py
├── style.css
├── background.jpg
├── README.md
├── .gitignore
├── my_whatsapp_data/ (added)
│   ├── _chat.txt
│   ├── [photos and videos]
│   └── ...
```

### Step 3: Run the Script

Run the Python script with your folder name as an argument (ensure you have Python 3 installed on your system):

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

## File Structure

After running the script, your directory structure should look like this:

```
whatsapp-beautifier/
├── whatsapp_beautifier.py
├── style.css
├── background.jpg
├── README.md
├── .gitignore
├── my_whatsapp_data/
│   ├── _chat.txt
│   ├── [photos and videos]
│   └── ...
└── my_whatsapp_data_chat.html (generated)
```
