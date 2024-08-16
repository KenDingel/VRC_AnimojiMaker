import os
import asyncio
from wand.image import Image
import requests
import logging
import subprocess

logger = logging.getLogger(__name__)

async def process_gif(url, temp_dir, settings):
    logger.info(f'Processing GIF: {url}')
    print(f'Processing GIF: {url}')
    gif_path = download_file(url, temp_dir, 'input.gif')
    sprite_sheet_path, info = create_sprite_sheet(gif_path, temp_dir, settings)
    return sprite_sheet_path, info

async def process_mp4(url, temp_dir, settings):
    logger.info(f'Processing MP4: {url}')
    print(f'Processing MP4: {url}')
    mp4_path = download_file(url, temp_dir, 'input.mp4')
    gif_path = convert_mp4_to_gif(mp4_path, temp_dir)
    sprite_sheet_path, info = create_sprite_sheet(gif_path, temp_dir, settings)
    return sprite_sheet_path, info

def download_file(url, temp_dir, filename):
    logger.info(f'Downloading file: {url}')
    print(f'Downloading file: {url}')
    response = requests.get(url)
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, 'wb') as f:
        f.write(response.content)
    logger.info(f'File downloaded: {file_path}')
    print(f'File downloaded: {file_path}')
    return file_path

def convert_mp4_to_gif(mp4_path, temp_dir):
    logger.info(f'Converting MP4 to GIF: {mp4_path}')
    print(f'Converting MP4 to GIF: {mp4_path}')
    gif_path = os.path.join(temp_dir, 'converted.gif')
    cmd = [
        'ffmpeg',
        '-i', mp4_path,
        '-vf', 'fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
        '-loop', '0',
        gif_path
    ]
    subprocess.run(cmd, check=True)
    logger.info(f'MP4 converted to GIF: {gif_path}')
    print(f'MP4 converted to GIF: {gif_path}')
    return gif_path

def create_sprite_sheet(gif_path, temp_dir, settings):
    logger.info(f'Creating sprite sheet from: {gif_path}')
    print(f'Creating sprite sheet from: {gif_path}')
    
    info = {}
    
    with Image(filename=gif_path) as img:
        # Get original FPS and dimensions
        original_fps = img.delay
        if original_fps == 0:
            original_fps = 10  # Default to 10 FPS if not specified
        else:
            original_fps = 100 // original_fps  # Convert centiseconds to FPS
        
        original_width, original_height = img.width, img.height
        original_frame_count = len(img.sequence)
        
        # Convert sequence to a list if it's not already
        img_sequence = list(img.sequence)
        
        # Limit to 64 frames
        img_sequence = img_sequence[:64]
        
        # Apply user settings
        if settings.get('frame_count'):
            img_sequence = img_sequence[:min(settings['frame_count'], 64)]
        
        # Determine tile configuration based on frame count
        frame_count = len(img_sequence)
        if frame_count <= 4:
            tile = "2x2"
            frame_size = 512
        elif frame_count <= 16:
            tile = "4x4"
            frame_size = 256
        else:
            tile = "8x8"
            frame_size = 128
        
        # Override with user settings if provided
        tile = settings.get('tile', tile)
        cols, rows = map(int, tile.split('x'))
        
        # Create a new blank image with white background
        with Image(width=cols*frame_size, height=rows*frame_size, background='transparent') as canvas:
            for i, frame in enumerate(img_sequence):
                with frame.clone() as f:
                    # Remove alpha channel to eliminate transparency
                    if f.alpha_channel:
                        f.background_color = 'transparent'
                        f.alpha_channel = 'activate'
                    
                    # Calculate scaling factor to fit within frame_size while maintaining aspect ratio
                    scale = min(frame_size / f.width, frame_size / f.height)
                    new_width = int(f.width * scale)
                    new_height = int(f.height * scale)
                    
                    # Resize frame while maintaining aspect ratio
                    f.resize(width=new_width, height=new_height, filter='lanczos')
                    
                    # Calculate position to center the frame within its cell
                    row = i // cols
                    col = i % cols
                    x = col * frame_size + (frame_size - new_width) // 2
                    y = row * frame_size + (frame_size - new_height) // 2
                    
                    # Composite the frame onto the canvas
                    canvas.composite(f, left=x, top=y)
            
            # Generate filename
            fps = settings.get('fps', original_fps)
            filename = f"SpriteSheet_{frame_count}frames_{fps}fps.png"
            sprite_sheet_path = os.path.join(temp_dir, filename)
            canvas.save(filename=sprite_sheet_path)
        
        # Collect information
        info['original_dimensions'] = f"{original_width}x{original_height}"
        info['original_frame_count'] = original_frame_count
        info['original_fps'] = original_fps
        info['final_frame_count'] = frame_count
        info['final_fps'] = fps
        info['frames_cropped'] = original_frame_count - frame_count if original_frame_count > frame_count else 0
        info['scaled'] = (new_width != original_width) or (new_height != original_height)
        info['final_frame_size'] = f"{new_width}x{new_height}"
        info['tile_configuration'] = tile
        
        logger.info(f'Sprite sheet saved: {sprite_sheet_path}')
        print(f'Sprite sheet saved: {sprite_sheet_path}')
        
        # Verify file existence
        if not os.path.exists(sprite_sheet_path):
            raise FileNotFoundError(f"Sprite sheet not found at {sprite_sheet_path}")
        
        return sprite_sheet_path, info