from pyrogram.types import Message
from pyrogram import Client
import asyncio
from utils.Database import save_file
from utils.Client import get_least_used_token_and_channel, remove_client
from config import STORAGE_CHANNEL_1, STORAGE_CHANNEL_2
from pyrogram.errors import FloodWait
import aiohttp
from utils.Downloader import get_file_bytes
from utils.Logger import Logger
from utils.other import break_list, get_file_size

logger = Logger(__name__)


async def send_file(session: aiohttp.ClientSession, file: str | bytes, bytes=False):
    data = {}
    if not bytes:
        with open(file, "rb") as file:
            data["document"] = file.read()
    else:
        data["document"] = file

    err = 0

    while err < 5:
        try:
            bot_token, channel = get_least_used_token_and_channel()
            if int(channel) == 1:
                data["chat_id"] = str(STORAGE_CHANNEL_1)
            elif int(channel) == 2:
                data["chat_id"] = str(STORAGE_CHANNEL_2)

            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
            async with session.post(url, data=data) as resp:
                if resp.status != 200:
                    try:
                        x = await resp.text()
                        logger.error(x)
                    except:
                        pass
                    raise Exception("Error while sending file to telegram")

                response = await resp.json()

                if not response["ok"]:
                    logger.error(response)
                    raise Exception("Error while sending file to telegram")

                return response["result"], channel
        except Exception as e:
            logger.error(e)
            err += 1

            await remove_client(bot_token)
            continue
    raise Exception("Failed to send file to telegram")


UPLOAD_PROGRESS = {}
ERR_CACHE = []


async def Start_TS_Uploader(session: aiohttp.ClientSession, tsFiles: list, hash: str):
    global UPLOAD_PROGRESS, ERR_CACHE

    tsData = {}
    new_file_list = []

    for ts_path in tsFiles:
        if hash in ERR_CACHE:
            return
        ts_name = ts_path.split("/")[-1]

        if get_file_size(ts_path) > 19.9 * 1024 * 1024:
            ERR_CACHE.append(hash)
            raise Exception(
                "Too high video bitrate !!! Compress your video first before conversion."
            )
        err_count = 0
        while True:
            if err_count == 5:
                raise Exception("Failed to upload ts file...")
            try:
                msg, channel = await send_file(session, ts_path)
                new_ts_name = ts_name.replace(".ts", f"_c{channel}.ts")
                tsData[new_ts_name] = msg["message_id"]
                new_file_list.append((ts_name, new_ts_name))
                UPLOAD_PROGRESS[hash] += 1
                break
            except FloodWait as e:
                logger.error(f"FloodWait Error : {e}")
                await asyncio.sleep(e.value)
                continue
            except Exception as e:
                err_count += 1
                logger.error(f"Error while uploading ts file {e}")

    return tsData, new_file_list


async def Start_TS_DL_And_Uploader(
    session: aiohttp.ClientSession, tsFiles: list, hash: str, headers: dict
):
    global UPLOAD_PROGRESS, ERR_CACHE

    tsData = {}
    new_file_list = []

    for ts_name, ts_url in tsFiles:
        if hash in ERR_CACHE:
            return
        try:
            file_bytes = await get_file_bytes(session, ts_url, headers=headers)
        except Exception as e:
            ERR_CACHE.append(hash)
            raise Exception(e)

        err_count = 0
        while True:
            if err_count == 5:
                raise Exception("Failed to upload ts file...")
            try:
                msg, channel = await send_file(session, file_bytes, bytes=True)
                ts_name = ts_name.replace(".ts", f"_c{channel}.ts")
                tsData[ts_name] = msg["message_id"]
                new_file_list.append((ts_name, ts_url))
                UPLOAD_PROGRESS[hash] += 1
                break
            except FloodWait as e:
                logger.error(f"FloodWait Error : {e}")
                await asyncio.sleep(e.value)
                continue
            except Exception as e:
                err_count += 1
                logger.error(f"Error while uploading ts file {e}")

    return tsData, new_file_list


async def ProgressUpdater(proc: Message, hash: str, total: int, name: str):
    global UPLOAD_PROGRESS, ERR_CACHE

    while UPLOAD_PROGRESS[hash] != total:
        if hash in ERR_CACHE:
            break
        await asyncio.sleep(10)
        try:
            await proc.edit_text(
                f"📤 **Uploading {name}**\n\n🧲 **Uploaded {UPLOAD_PROGRESS[hash]} / {total} ts files**\n\n⚠️ **Note :** If the file is too large, it may take some time to upload all files. Please be patient."
            )
        except Exception as e:
            logger.warning(e)


async def Multi_TS_File_Uploader(session, data: list, proc: Message, hash: str):
    global UPLOAD_PROGRESS, ERR_CACHE

    total = len(data)
    breaked_data = break_list(data, total // 10)  # break data into 10 parts

    tasks = [asyncio.create_task(ProgressUpdater(proc, hash, total, "Video"))]
    for i in breaked_data:
        tasks.append(asyncio.create_task(Start_TS_Uploader(session, i, hash)))

    UPLOAD_PROGRESS[hash] = 0
    results = await asyncio.gather(*tasks, return_exceptions=True)
    if any(isinstance(result, Exception) for result in results):
        for task in tasks:
            task.cancel()  # Send cancel request to each task
        await asyncio.gather(
            *tasks, return_exceptions=True
        )  # Wait for all tasks to handle their cancellation

        raise Exception("Failed To Upload Video")

    combined_ts_data = {}
    new_file_list = []
    for i, k in results[1:]:
        combined_ts_data.update(i)
        new_file_list.extend(k)

    return combined_ts_data, new_file_list


async def Multi_TS_DL_And_Uploader(
    session: aiohttp.ClientSession,
    file_list: list,
    proc: Message,
    hash: str,
    name: str,
    headers: dict,
):
    global UPLOAD_PROGRESS, ERR_CACHE

    total = len(file_list)
    breaked_data = break_list(file_list, total // 10)  # break data into 10 parts

    tasks = [asyncio.create_task(ProgressUpdater(proc, hash, len(file_list), name))]
    for i in breaked_data:
        tasks.append(
            asyncio.create_task(Start_TS_DL_And_Uploader(session, i, hash, headers))
        )

    UPLOAD_PROGRESS[hash] = 0
    results = await asyncio.gather(*tasks, return_exceptions=True)
    if any(isinstance(result, Exception) for result in results):
        for task in tasks:
            task.cancel()  # Send cancel request to each task
        await asyncio.gather(
            *tasks, return_exceptions=True
        )  # Wait for all tasks to handle their cancellation

        raise Exception("Failed To Upload Video")

    combined_ts_data = {}
    new_file_list = []
    for i, k in results[1:]:
        combined_ts_data.update(i)
        new_file_list.extend(k)

    print(combined_ts_data, new_file_list)

    return combined_ts_data, new_file_list
