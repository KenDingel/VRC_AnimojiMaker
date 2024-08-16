# VRC_AnimojiMaker

## Authors: coolkiwiii and Ken (alphabetically)


This Discord bot converts GIFs and MP4 files into sprite sheets for use as animated emojis in VRChat! Works with uploaded files, links, or GIFs from the Discord GIF menu! The bot also provides detailed information in a pretty embed :)

## Features

- Converts GIFs and MP4 files into sprite sheets for VRChat animated emojis.
- Supports direct file uploads and links (including Tenor GIFs from the Discord GIF Menu).
- Automatically determines the correct frame count and FPS.
- Maintains aspect ratio and centers frames within cells.
- Provides detailed information about the conversion process.
- Sends results as a *pretty* embed message with the sprite sheet image.

## Requirements

- Python 3.9+
- Required Python packages (see below!)
- [FFmpeg](https://ffmpeg.org/download.html)
- [ImageMagick](https://imagemagick.org/script/download.php)

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/KenDingel/VRC_AnimojiMaker.git
   cd VRC_AnimojiMaker
   ```

2. **Install the required Python packages:**
   ```bash
   pip install Wand nextcord requests beautifulsoup4
   ```

3. **Install FFmpeg and ImageMagick:**
   - **Windows:**
     - FFmpeg: [Download from ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.
     - ImageMagick: Use the [instructions provided by Wand](https://docs.wand-py.org/en/0.6.12/guide/install.html) for proper set up! BE SURE TO INSTALL DEV C++ IN THE INSTALL!
   - **macOS (using Homebrew):**
     ```bash
     brew install ffmpeg imagemagick
     ```
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt-get update
     sudo apt-get install ffmpeg imagemagick
     ```

4. **Create a `config.json` file in the project root:**
   ```json
   {
     "token": "YOUR_BOT_TOKEN_HERE",
     "channel_id": YOUR_CHANNEL_ID_HERE,
     "log_file": "bot.log"
   }
   ```
   Replace `YOUR_BOT_TOKEN_HERE` with your Discord bot token and `YOUR_CHANNEL_ID_HERE` with the ID of the channel where the bot should operate.

## Usage

1. **Run the bot:**
   ```bash
   python run_me_for_gif_fun.py
   ```

2. **Use the bot in the designated Discord channel:**
   - Upload a GIF or MP4 file directly.
   - Send a link to a GIF or MP4 file.
   - Send a Tenor GIF link via the Discord GIF menu.

3. **The bot will process the file and reply with:**
   - An embed message containing detailed information about the conversion.
   - The generated sprite sheet image.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## VRChat Guidelines

When using the generated sprite sheets in VRChat, ensure they comply with VRChat's content guidelines. Content should be safe for work and not include any inflammatory or suggestive material.
