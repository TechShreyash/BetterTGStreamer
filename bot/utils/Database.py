from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URL
from utils.Logger import Logger

logger = Logger(__name__)

db = AsyncIOMotorClient(MONGO_DB_URL)["BetterTGStreamer"]

filesDB = db["files"]


async def save_file(hash: str, tsData: dict, subtitles: dict = {}):
    try:
        await filesDB.insert_one(
            {"hash": hash, "tsData": tsData, "subtitles": subtitles}
        )
    except Exception as e:
        logger.error(e)


async def is_hash_used(hash: str):
    try:
        x = await filesDB.find_one({"hash": hash})
        if x:
            return True
        return False
    except Exception as e:
        logger.error(e)
