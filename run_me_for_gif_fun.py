import nextcord
from nextcord.ext import commands
import json
import logging
import re
import os
import requests
import traceback
from bs4 import BeautifulSoup
from gif_processor import process_gif, process_mp4
from utils import setup_logging, create_temp_dir, cleanup_temp_dir

# Load configuration
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize bot
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Bot is ready. Logged in as {bot.user.name}')
    print(f'Bot is ready. Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CONFIG['channel_id']:
        logger.info(f'Message received in non-target channel. Channel ID: {message.channel.id}')
        return

    logger.info(f'Processing message from {message.author}: {message.content}')
    print(f'Processing message from {message.author}: {message.content}')

    # Extract user settings from the message
    settings = extract_settings(message.content)

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('.gif', '.mp4')):
                logger.info(f'Found attachment: {attachment.filename}')
                print(f'Found attachment: {attachment.filename}')
                await process_file_message(message, attachment.url, attachment.filename, settings)
    elif "tenor.com" in message.content:
        logger.info(f'Found Tenor link in message: {message.content}')
        print(f'Found Tenor link in message: {message.content}')
        media_url, media_type = await extract_tenor_media_url(message.content)
        if media_url:
            await process_file_message(message, media_url, f'tenor_media.{media_type}', settings)
    elif message.content.startswith('http') and message.content.lower().endswith(('.gif', '.mp4')):
        logger.info(f'Found direct URL in message: {message.content}')
        print(f'Found direct URL in message: {message.content}')
        await process_file_message(message, message.content, message.content.split('/')[-1], settings)

    await bot.process_commands(message)

def extract_settings(content):
    settings = {}
    # Extract frame count
    frame_count_match = re.search(r'frames:(\d+)', content)
    if frame_count_match:
        settings['frame_count'] = int(frame_count_match.group(1))
    
    # Extract tile configuration
    tile_match = re.search(r'tile:(\d+x\d+)', content)
    if tile_match:
        settings['tile'] = tile_match.group(1)
    
    # Extract FPS
    fps_match = re.search(r'fps:(\d+)', content)
    if fps_match:
        settings['fps'] = int(fps_match.group(1))
    
    return settings

async def process_file_message(message, url, filename, settings):
    await message.add_reaction('⏳')
    temp_dir = create_temp_dir()
    logger.info(f'Created temporary directory: {temp_dir}')
    print(f'Created temporary directory: {temp_dir}')

    try:
        if filename.lower().endswith('.gif') or (filename.startswith('tenor_media') and filename.endswith('.gif')):
            sprite_sheet, info = await process_gif(url, temp_dir, settings)
        elif filename.lower().endswith('.mp4') or (filename.startswith('tenor_media') and filename.endswith('.mp4')):
            sprite_sheet, info = await process_mp4(url, temp_dir, settings)
        else:
            raise ValueError(f'Unsupported file type: {filename}')

        logger.info(f'Processed file. Sending sprite sheet: {sprite_sheet}')
        print(f'Processed file. Sending sprite sheet: {sprite_sheet}')
        
        if not os.path.exists(sprite_sheet):
            raise FileNotFoundError(f"Sprite sheet not found at {sprite_sheet}")
        
        # Create and send the embed message
        embed = create_info_embed(info, filename)
        await message.channel.send(embed=embed)
        
        # Send the sprite sheet
        await message.channel.send(file=nextcord.File(sprite_sheet))
        await message.add_reaction('✅')
    except FileNotFoundError as e:
        logger.error(f'Sprite sheet not found: {str(e)}')
        print(f'Sprite sheet not found: {str(e)}')
        await message.add_reaction('💀')
        await message.channel.send(f'Error: Sprite sheet could not be created. Please try again.')
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f'Error processing file: {str(e)} TRACEBACK: {tb}')
        print(f'Error processing file: {str(e)}')
        await message.add_reaction('💀')
        await message.channel.send(f'Error processing file: {str(e)}')
    finally:
        cleanup_temp_dir(temp_dir)
        logger.info(f'Cleaned up temporary directory: {temp_dir}')
        print(f'Cleaned up temporary directory: {temp_dir}')

def create_info_embed(info, filename):
    embed = nextcord.Embed(title="Sprite Sheet Information", color=0x00ff00)
    embed.add_field(name="Original File", value=filename, inline=False)
    embed.add_field(name="Original Dimensions", value=info['original_dimensions'], inline=True)
    embed.add_field(name="Original Frame Count", value=str(info['original_frame_count']), inline=True)
    embed.add_field(name="Original FPS", value=str(info['original_fps']), inline=True)
    embed.add_field(name="Final Frame Count", value=str(info['final_frame_count']), inline=True)
    embed.add_field(name="Final FPS", value=str(info['final_fps']), inline=True)
    embed.add_field(name="Frames Cropped", value=str(info['frames_cropped']), inline=True)
    embed.add_field(name="Scaled", value="Yes" if info['scaled'] else "No", inline=True)
    embed.add_field(name="Final Frame Size", value=info['final_frame_size'], inline=True)
    embed.add_field(name="Tile Configuration", value=info['tile_configuration'], inline=True)
    return embed

async def extract_tenor_media_url(tenor_url):
    logger.info(f'Extracting media URL from Tenor link: {tenor_url}')
    print(f'Extracting media URL from Tenor link: {tenor_url}')
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(tenor_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the Gif div
        gif_div = soup.find('div', class_='Gif')
        if gif_div:
            # Try to find the img tag within the Gif div
            img_tag = gif_div.find('img')
            if img_tag and img_tag.has_attr('src'):
                media_url = img_tag['src']
                media_type = 'gif'
            else:
                # If img tag is not found, look for a video tag
                video_tag = gif_div.find('video')
                if video_tag:
                    source_tag = video_tag.find('source')
                    if source_tag and source_tag.has_attr('src'):
                        media_url = source_tag['src']
                        media_type = 'mp4'
                    else:
                        logger.warning('Could not find source tag in video')
                        return None, None
                else:
                    logger.warning('Could not find img or video tag in Gif div')
                    return None, None
            
            logger.info(f'Extracted media URL: {media_url}')
            print(f'Extracted media URL: {media_url}')
            return media_url, media_type

        logger.warning('Could not find Gif div')
        return None, None
    except Exception as e:
        logger.error(f'Error extracting media URL from Tenor link: {str(e)}')
        print(f'Error extracting media URL from Tenor link: {str(e)}')
        return None, None

bot.run(CONFIG['token'])