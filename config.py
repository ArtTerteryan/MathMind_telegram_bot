import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Logger setup
logging.basicConfig(
    level=logging.INFO,  # Adjust level as needed
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432)),  # Adjust the default port if necessary
}

# Telegram bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Valid sub-question numbers
VALID_SUBQUESTIONS = ['1', '2', '3', '4']

# Check for missing environment variables
missing_vars = []
for key, value in DB_CONFIG.items():
    if not value:
        missing_vars.append(key)
if not BOT_TOKEN:
    missing_vars.append('BOT_TOKEN')
if missing_vars:
    logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
    exit(1)
