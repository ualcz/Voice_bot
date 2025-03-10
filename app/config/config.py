import os
from dotenv import load_dotenv

load_dotenv()

# Bot configurations
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DB_DSN = os.getenv('DATABASE_URL')
BOT_VERSION = '0.0.2'