from pyrogram.types import Message
import asyncio
import time, aiohttp, aiofiles
from utils.Logger import Logger

logger = Logger(__name__)
T1_CACHE = {}


async def _download_progress(current, total, proc: Message, hash: str):
    global T1_CACHE

    t1 = T1_CACHE[hash]
    t2 = time.time()

    if (t2 - t1) > 10:
        current = round(current / (1024 * 1024))  # MB
        total = round(total / (1024 * 1024))  # MB
        try:
            await proc.edit(f"📥 **Downloaded {current} / {total} MB**")
            T1_CACHE[hash] = time.time()
        except Exception as e:
            logger.warning(e)


async def TG_Downloader(file_msg: Message, proc: Message, hash: str, file_path: str):
    global T1_CACHE

    await asyncio.sleep(1)
    logger.info(f"Downloading... {hash}")

    try:
        await proc.edit("📥 **Downloading File From Telegram...**")
    except Exception as e:
        logger.warning(e)

    T1_CACHE[hash] = time.time()
    await file_msg.download(
        file_path, progress=_download_progress, progress_args=(proc, hash)
    )

    try:
        await proc.edit("📥 **Download Completed**")
    except Exception as e:
        logger.warning(e)

    logger.info(f"Download Complete {hash}")
    await asyncio.sleep(1)


async def get_file_bytes(session, url, headers):
    async with session.get(url, headers=headers) as r:
        if r.status != 200:
            raise Exception("Failed To Download Video Segment")

        bytes_data = await r.read()

        file_size = int(r.headers.get("Content-Length", 0))
        if file_size == 0:
            file_size = len(bytes_data)

        if file_size > (19.5 * 1024 * 1024):
            raise Exception("Too High Video Bitrate")

        return bytes_data
