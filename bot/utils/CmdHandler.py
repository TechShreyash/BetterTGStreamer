from pyrogram import Client
from pyrogram.types import Message
from typing import Literal
from config import (
    TEST_MODE,
    MAX_ACTIVE_TASKS,
    VIDEO_STORAGE,
    MAX_USER_CONCURRENT_TASKS,
)
from utils.Queue import ACTIVE_USERS, add_to_queue, QUEUE_CACHE
from utils.Logger import Logger

logger = Logger(__name__)


async def check_file(
    client: Client, message: Message, _type: Literal["convert", "encode", "upload"]
):
    try:
        global ACTIVE_USERS, QUEUE_CACHE

        if not message.reply_to_message:
            return await message.reply_text(
                "📌 **Reply with this command to upload a video file**"
            )

        file = message.reply_to_message.video or message.reply_to_message.document

        if not file:
            return await message.reply_text(
                "📌 **Reply with this command to upload a video file**"
            )

        file_name = file.file_name
        if file_name:
            file_name = file_name.lower()
            if (not file_name.endswith(".mkv")) and (not file_name.endswith(".mp4")):
                return await message.reply_text(
                    "❌ **Supported Formats:** Only files with the extensions .mkv and .mp4 are accepted."
                )
        else:
            file_name = "video.mp4"

        mime_type = file.mime_type
        if (mime_type != "video/mp4") and (mime_type != "video/x-matroska"):
            return await message.reply_text(
                "❌ **Supported Formats:** Only files with the extensions .mkv and .mp4 are accepted."
            )

        file_size = file.file_size
        if not TEST_MODE:
            if file_size < 5 * 1024 * 1024:  # 5MB
                return await message.reply_text(
                    "❌ **File Size Requirement:** Files must be larger than 5MB to be processed."
                )

        if ACTIVE_USERS.count(message.from_user.id) >= MAX_USER_CONCURRENT_TASKS:
            return await message.reply_text(
                f"❌ **Processing Limit:** You can only process {MAX_USER_CONCURRENT_TASKS} videos simultaneously."
            )
        else:
            logger.info(f"User {message.from_user.id} added to active users")
            ACTIVE_USERS.append(message.from_user.id)

        file_msg = await client.copy_message(
            VIDEO_STORAGE,
            message.from_user.id,
            message.reply_to_message.id,
            f"User : {message.from_user.id}\n\nFile : {file_name}\n\n#VIDEO",
        )
        proc = await message.reply_text(
            f"🔄 **Task Added To Queue**\n\n📈 **Queue Position :** {len(QUEUE_CACHE)+1}\n\n🔆 **Check Queue Status :** /queue"
        )
        add_to_queue(message, proc, file_msg, _type)
    except Exception as e:
        logger.error(e)
        try:
            await message.reply_text(
                f"❌ **Error :** {e}\n\n**Try Again Or Contact @TechZBots_Support**"
            )
        except Exception as e:
            logger.debug(e)


async def convert_playerx(client: Client, message: Message):
    global ACTIVE_USERS, QUEUE_CACHE

    cmd = message.command
    if len(cmd) != 2:
        return await check_file(client, message, "convert")

    video_url = cmd[1]
    if (
        (not video_url.startswith("https://playerx.stream/v/"))
        and (not video_url.startswith("https://vectorx.top/v/"))
        and (not video_url.startswith("https://bestx.stream/v/"))
    ):
        return await check_file(client, message, "convert")

    if ACTIVE_USERS.count(message.from_user.id) >= MAX_USER_CONCURRENT_TASKS:
        return await message.reply_text(
            f"❌ **Processing Limit:** You can only process {MAX_USER_CONCURRENT_TASKS} videos simultaneously."
        )
    else:
        logger.info(f"User {message.from_user.id} added to active users")
        ACTIVE_USERS.append(message.from_user.id)

    proc = await message.reply_text(
        f"🔄 **Task Added To Queue**\n\n📈 **Queue Position :** {len(QUEUE_CACHE)+1}\n\n🔆 **Check Queue Status :** /queue"
    )

    add_to_queue(message, proc, None, "upload")


async def remote_url_upload(client, message: Message):
    global ACTIVE_USERS, QUEUE_CACHE

    cmd = message.command
    if len(cmd) != 2:
        return await message.reply_text(
            """🔗 **Upload Remote File For Encoding**

To upload a file, use the command /remote [file_url]

🌐 **Supported Hosts :** 

`FTP URL, Direct Link (M3U8), Google Drive, OneDrive, mediafire.com, Yandex Disk, FileSend.jp, OK.RU, Mail.Ru, VK.com, Gofile.io, Streamtape.com, Vimeo.com, Youtube.com, Streamlare.com, 1fichier.com, MEGA, DropMeFiles.com, TusFiles.com, MixDrop, FileMoon, FileLions, StreamWish, VOE.sx, TeraBox, Fembed, VidMoly, Uptobox, PornHub.com, XVIDEOS.COM, xHamster.com`

💠 **Supported URL Formats :** https://t.me/TechZBots/813
""",
            disable_web_page_preview=True,
        )

    if ACTIVE_USERS.count(message.from_user.id) >= MAX_USER_CONCURRENT_TASKS:
        return await message.reply_text(
            f"❌ **Processing Limit:** You can only process {MAX_USER_CONCURRENT_TASKS} videos simultaneously."
        )
    else:
        logger.info(f"User {message.from_user.id} added to active users")
        ACTIVE_USERS.append(message.from_user.id)

    proc = await message.reply_text(
        f"🔄 **Task Added To Queue**\n\n📈 **Queue Position :** {len(QUEUE_CACHE)+1}\n\n🔆 **Check Queue Status :** /queue"
    )

    add_to_queue(message, proc, None, "remote")
