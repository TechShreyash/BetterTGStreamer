# Telegram API ID and Hash
API_ID = int("telegram_api_id")
API_HASH = "telegram_api_hash"

# Bot which will handle users commands
MAIN_BOT_TOKEN = "main_bot_token"

LOGGER_BOT_TOKEN = "logger_bot_token"

# Bot tokens for STORAGE_CHANNEL_1, they all must be admin in the channel
UPLOADER_BOTS_1 = ["bot_token1", "bot_token2", "bot_token3"]

# Bot tokens for STORAGE_CHANNEL_2, they all must be admin in the channel
UPLOADER_BOTS_2 = ["bot_token4", "bot_token5", "bot_token6"]

# Telegram Channel ID where videos will be stored
VIDEO_STORAGE = -1001234567890
# Telegram Channel ID where logs will be stored
LOGGER_CHANNEL = -1001234567890
# Telegram Channel ID where m3u8 file will be stored
STORAGE_CHANNEL_1 = -1001234567890
STORAGE_CHANNEL_2 = -1001234567890

# Max no. of tasks to run simultaneously
MAX_ACTIVE_TASKS = 5

# Max no. of tasks a user can run simultaneously
MAX_USER_CONCURRENT_TASKS = 3

# No. of simulataneous uploaders to run per task for .ts file upload
NO_OF_UPLOADERS = 5

# In MB (MegaBytes). Size of each segment uploaded to telegram. Must be less than 10 MB
SEGMENT_SIZE = 2

# Telegram User ID of the bot owner
OWNER_ID = 1234567890

# Domain name of the website where the stream api is hosted
WEBSITE_DOMAIN = "https://stream.mywebsite.com"

# MongoDB Database URL
MONGO_DB_URL = "mongodb+srv://database:pass@cluster0.gdsgfg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Playerx.stream Login details
PLAYERX_EMAIL = "your_email@gmail.com"
PLAYERX_PASSWORD = "your_password"
PLAYERX_API_KEY = "your_api"
