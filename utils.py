import os
import tempfile
import shutil
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    print("Logging setup complete")

def create_temp_dir():
    temp_dir = tempfile.mkdtemp()
    print(f"Created temporary directory: {temp_dir}")
    return temp_dir

def cleanup_temp_dir(temp_dir):
    shutil.rmtree(temp_dir)
    print(f"Cleaned up temporary directory: {temp_dir}")