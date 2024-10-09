import re
import os
from PIL import Image
from telegram import InputFile
from config import logger

# Function to validate ID format
def validate_id_format(user_input):
    pattern = r'^\d+/\d+/\d+/\d+$'  # Allows IDs like x/x/x/x
    return bool(re.match(pattern, user_input))

# Function to validate image dimensions
def validate_image_dimensions(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            logger.info(f"Image dimensions for {image_path}: {width}x{height}")

            # Define aspect ratio threshold (e.g., width shouldn't be more than 10x the height)
            aspect_ratio = width / height

            if width > 2000 or aspect_ratio > 10:  # Adjust as needed
                logger.error(f"Problematic image dimensions: {width}x{height} (Aspect ratio: {aspect_ratio})")
                return False

            return True
    except Exception as e:
        logger.error(f"Failed to validate image dimensions: {e}")
        return False

# Resize the image if it's too wide
def resize_image(image_path, max_width=2000, min_height=150):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            resized = False  # Flag to track if resizing was performed

            # Resize width if it's larger than max_width
            if width > max_width:
                new_height = int((max_width / width) * height)
                img = img.resize((max_width, new_height))
                logger.info(f"Image resized by width to {max_width}x{new_height}")
                resized = True

            # If the height is smaller than the minimum allowed, increase the height
            if height < min_height:
                # Calculate the new width based on the new height to maintain the aspect ratio
                new_width = int((min_height / height) * width)
                img = img.resize((new_width, min_height))
                logger.info(f"Image resized by height to {new_width}x{min_height}")
                resized = True

            # Only save the image if it was resized
            if resized:
                img.save(image_path)
                logger.info(f"Image saved after resizing to {img.size}")

            return True
    except Exception as e:
        logger.error(f"Failed to resize image: {e}")
        return False

# Function to handle problematic images (validate and resize)
def handle_problematic_image(image_path):
    if not validate_image_dimensions(image_path):
        resize_image(image_path)
    return image_path

# Helper function to send images with error handling
async def send_image(update, image_path: str):
    try:
        image_path = handle_problematic_image(image_path)

        if image_path.startswith('http://') or image_path.startswith('https://'):
            await update.message.reply_photo(photo=image_path)
        else:
            if not os.path.isfile(image_path):
                logger.error(f'Image file not found: {image_path}')
                await update.message.reply_text('Image not found on the server.')
                return

            with open(image_path, 'rb') as image_file:
                await update.message.reply_photo(photo=InputFile(image_file))
    except Exception as e:
        logger.error(f'Error sending image: {e}', exc_info=True)
        await update.message.reply_text('An error occurred while sending the image. Please try again later.')
