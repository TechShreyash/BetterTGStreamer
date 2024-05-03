from config import (
    API_ID,
    API_HASH,
    MAIN_BOT_TOKEN,
    UPLOADER_BOTS_1,
    UPLOADER_BOTS_2,
    LOGGER_BOT_TOKEN,
)
from pyrogram import Client
from utils.Logger import Logger

app = Client(
    "main_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=MAIN_BOT_TOKEN,
)
logger_bot = Client(
    "logger_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=LOGGER_BOT_TOKEN,
)
UPLOADER_CLIENTS = {}  # {num : {usage: 0,token: bot_token}}
logger = Logger(__name__)


def get_least_used_token_and_channel() -> Client:
    global UPLOADER_CLIENTS

    least_used_client = min(
        UPLOADER_CLIENTS, key=lambda x: UPLOADER_CLIENTS[x]["usage"]
    )
    UPLOADER_CLIENTS[least_used_client]["usage"] += 1
    token, channel = UPLOADER_CLIENTS[least_used_client]["token"].split("%*^")
    return token, channel


async def remove_client(token):
    await app.send_message("TechShreyash", f"Token Error : {token} ")


async def start_clients():
    global UPLOADER_CLIENTS

    logger.info("Starting Bots...")
    await app.start()
    await logger_bot.start()
    logger.info("Bot Started!")

    pos = 0
    for token in UPLOADER_BOTS_1:
        pos += 1
        UPLOADER_CLIENTS[pos] = {
            "usage": 0,
            "token": token + "%*^1",
        }
    for token in UPLOADER_BOTS_2:
        pos += 1
        UPLOADER_CLIENTS[pos] = {
            "usage": 0,
            "token": token + "%*^2",
        }

    logger.info(f"Added {pos} Uploader Bots!")
