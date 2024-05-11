from pyrogram.types import Message
from pyrogram.errors import MessageTooLong
import asyncio
from utils.Database import is_hash_used
from utils.Downloader import TG_Downloader
from utils.M3u8Handler import Master_Handler, Single_M3U8_Uploader
from utils.Transcoder import transcode_video
from utils.other import create_directory, random_string
from config import MAX_ACTIVE_TASKS, WEBSITE_DOMAIN
import shutil
from utils.Playerxstream import PlayerxStream
import aiohttp
from typing import Literal
from utils.Logger import Logger

logger = Logger(__name__)

QUEUE_CACHE = []
ACTIVE_USERS = []
ACTIVE_TASKS = 0

playerxstream = PlayerxStream()


def add_to_queue(
    message: Message,
    proc: Message,
    file_msg: Message | None,
    _type: Literal["convert", "encode", "upload", "remote"],
):
    global QUEUE_CACHE

    QUEUE_CACHE.append(
        {"message": message, "proc": proc, "file_msg": file_msg, "type": _type}
    )


def get_active_task():
    global ACTIVE_TASKS
    return ACTIVE_TASKS


async def queue_handler():
    global QUEUE_CACHE, ACTIVE_TASKS, ACTIVE_USERS

    while True:

        while len(QUEUE_CACHE) > 0:
            if ACTIVE_TASKS >= MAX_ACTIVE_TASKS:
                break

            data = QUEUE_CACHE.pop(0)
            try:
                # start processing video
                asyncio.create_task(
                    process_video(
                        data["message"], data["proc"], data["file_msg"], data["type"]
                    )
                )
            except Exception as e:
                ACTIVE_TASKS -= 1
                ACTIVE_USERS.remove(data["message"].from_user.id)

                logger.error(e)
                try:
                    await data["proc"].edit_text(
                        f"❌ **Error :** {e}\n\n**Try Again Or Contact @TechZBots_Support**"
                    )
                except Exception as e:
                    logger.warning(e)

        await asyncio.sleep(10)


async def process_video(
    message: Message,
    proc: Message,
    file_msg: Message | None,
    _type: Literal["convert", "encode", "upload", "remote"],
):
    global ACTIVE_USERS, ACTIVE_TASKS, ACTIVE_USERS
    ACTIVE_TASKS += 1

    try:
        while True:
            hash = random_string(10)
            if not await is_hash_used(hash):
                break

        if _type == "convert" or _type == "encode":
            file = message.reply_to_message.video or message.reply_to_message.document
            file_name = file.file_name
            if file_name:
                file_name = file_name.lower()
                extension = file_name.split(".")[-1]
            else:
                mime_type = file.mime_type
                if mime_type == "video/mp4":
                    extension = "mp4"
                elif mime_type != "video/x-matroska":
                    extension = "mkv"

        create_directory(hash)

        logger.info(f"Processing... {hash}")
        try:
            await proc.edit_text(
                "🔄 **Processing...**",
            )
        except Exception as e:
            logger.warning(e)
        await asyncio.sleep(1)

        session = aiohttp.ClientSession()

        if _type == "convert" or _type == "encode":
            file_path = f"files/{hash}/{hash}.{extension}"
            await TG_Downloader(file_msg, proc, hash, file_path)

        if _type == "convert":
            m3u8_file = f"files/{hash}/index.m3u8"
            status, err = await transcode_video(file_path, m3u8_file, hash, proc)
            if not status:
                raise err  # exit if transcoding failed

            m3u8 = await Single_M3U8_Uploader(session, proc, m3u8_file, hash)

            await message.reply_text(
                f"⭐️ **M3u8 Url Generated Successfully**\n\n🖥 **Stream Link :** {WEBSITE_DOMAIN}/embed/{hash}/{m3u8}\n\n📁 **M3u8 Link :** {WEBSITE_DOMAIN}/file/{hash}/{m3u8}\n\n⚠️ **Note :** If stream link doesnt work, open m3u8 link in VLC Player, MX Player or any other m3u8 supported player."
            )
            logger.info(f"M3u8 Url : {WEBSITE_DOMAIN}/file/{hash}/{m3u8}")

        elif _type == "upload":
            video_url = message.command[1]
            data, headers = await playerxstream.extract_video(session, video_url, hash)
            subtitle_text, m3u8 = await Master_Handler(
                session, proc, data, headers, hash
            )

            if subtitle_text != "":
                subtitle_text = f"{subtitle_text}\n\n"

            try:
                await message.reply_text(
                    f"⭐️ **M3u8 Url Generated Successfully**\n\n🖥 **Stream Link :** {WEBSITE_DOMAIN}/embed/{hash}/{m3u8}\n\n📁 **M3u8 Link :** {WEBSITE_DOMAIN}/file/{hash}/{m3u8}\n\n{subtitle_text}⚠️ **Note :** If stream link doesnt work, open m3u8 link in VLC Player, MX Player or any other m3u8 supported player."
                )
            except MessageTooLong:
                with open(f"files/{hash}/{hash}_subtitle_links.txt", "w") as f:
                    f.write(subtitle_text)
                message = await message.reply_text(
                    f"⭐️ **M3u8 Url Generated Successfully**\n\n🖥 **Stream Link :** {WEBSITE_DOMAIN}/embed/{hash}/{m3u8}\n\n📁 **M3u8 Link :** {WEBSITE_DOMAIN}/file/{hash}/{m3u8}\n\n⚠️ **Note :** If stream link doesnt work, open m3u8 link in VLC Player, MX Player or any other m3u8 supported player."
                )
                await message.reply_document(
                    document=f"files/{hash}/{hash}_subtitle_links.txt",
                    caption="🗒 This file contains subtitle links, which can be externally loaded into your video player.\n\nAlternatively, you can use the stream link to automatically load the subtitles.",
                )

            logger.info(f"M3u8 Url : {WEBSITE_DOMAIN}/file/{hash}/{m3u8}")

        elif _type == "encode":
            # upload files to doodstream for processing video
            video_url = await playerxstream.upload_file(session, file_path, proc, hash)

        elif _type == "remote":
            file_url = message.command[1]
            video_url = await playerxstream.url_upload(session, file_url, proc, hash)

        if _type == "encode" or _type == "remote":
            try:
                await proc.edit(
                    f"🖥 **Waiting For Encoding To Complete...**\n\n⚠️ **Note:** You will be notified once encoding is finished. Please wait patiently, this will take time."
                )
            except Exception as e:
                logger.warning(e)

            await asyncio.sleep(1)
            last_p = 0
            while True:
                await asyncio.sleep(30)
                status, progress = await playerxstream.is_video_ready(
                    session, video_url
                )
                if status == "ACTIVE":
                    break
                elif status == "ERROR":
                    raise Exception("Encoding Failed")

                if last_p != progress:
                    last_p = progress
                    try:
                        await proc.edit(
                            f"🖥 **Encoding Your Video**\n\n⏰ **Status :** {status}\n\n📈 **Progress :** {progress}\n\n⚠️ **Note:** You will be notified once encoding is finished. Please wait patiently, this will take time."
                        )
                    except Exception as e:
                        logger.warning(e)

            await message.reply_text(
                f"✅ **Video Encoded Successfully :** {video_url}\n\n**Send** `/convert {video_url}` **to upload and save encoded file to telegram, And get m3u8 url.**"
            )
        await session.close()

        try:
            await proc.delete()
        except Exception as e:
            logger.warning(e)

    except Exception as e:
        logger.error(f"{hash} : {e}")
        try:
            await proc.edit_text(
                f"❌ **Error :** {e}\n\n**Try Again Or Contact @TechZBots_Support**",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.warning(e)
            try:
                await message.reply_text(
                    f"❌ **Error :** {e}\n\n**Try Again Or Contact @TechZBots_Support**",
                    disable_web_page_preview=True,
                )
            except Exception as e:
                logger.warning(e)

    try:
        shutil.rmtree(f"files/{hash}")
    except Exception as e:
        pass

    ACTIVE_TASKS -= 1
    ACTIVE_USERS.remove(message.from_user.id)
