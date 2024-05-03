import sys, asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from utils.Playerxstream import playerxstream_updater
from utils.other import reset_directory
from utils.Client import app, start_clients, logger_bot
from utils.Queue import get_active_task, queue_handler, ACTIVE_USERS
from config import OWNER_ID
from utils.Logger import Logger, log_updater
from utils.CmdHandler import check_file, convert_playerx, remote_url_upload

logger = Logger(__name__)


@app.on_message(filters.command("start") & filters.private & filters.incoming)
async def start(client: Client, message: Message):
    await message.reply_text(
        """💠 **Enhance Your Streaming with Better TG Streamer Bot**

Transform MP4 and MKV files into smooth M3U8 HLS streams! Remote URL uploading is supported from various hosts, including FTP, Direct Links, Google Drive, OneDrive, and more. Enjoy unlimited file uploads and permanent file links.

👉 Click /help for quick commands.

🆘 Need help? Join our support group: **@TechZBots_Support**.

**Made with ❤️ by @TechZBots**.
"""
    )


@app.on_message(filters.command("help") & filters.private & filters.incoming)
async def help(client: Client, message: Message):
    await message.reply_text(
        """🤖 **Better TG Streamer Bot Help**

Here are the commands you can use to unleash the full potential of Better TG Streamer Bot:

1. **/convert**: Convert Video To M3u8
   - **Speed**: Fast
   - **Quality**: Original
   - **Features**: Supports Multiple Audio Tracks

2. **/encode**: Encode Video To M3u8
   - **Speed**: Slow
   - **Quality**: Multiple Options Available
   - **Features**: Supports Multiple Audio Tracks and Subtitles (H.264/AAC)

3. **/remote**: Upload Remote File For Encoding
   - **Supported Hosts**: Click /remote to view the list of supported hosts

4. **/queue**: Check Queue Status
   - **Status**: Displays Processing and Queued Tasks

Type any of these commands to perform the respective action. Enjoy seamless streaming with Better TG Streamer Bot!
"""
    )


@app.on_message(filters.command("convert") & filters.private & filters.incoming)
async def _convert(client: Client, message: Message):
    return await convert_playerx(client, message)


@app.on_message(filters.command("encode") & filters.private & filters.incoming)
async def _encode(client: Client, message: Message):
    return await check_file(client, message, "encode")


@app.on_message(filters.command("remote") & filters.private & filters.incoming)
async def _remote(client: Client, message: Message):
    return await remote_url_upload(
        client,
        message,
    )


@app.on_message(filters.command("queue") & filters.private & filters.incoming)
async def queue(client: Client, message: Message):
    global ACTIVE_USERS

    x = get_active_task()
    y = ACTIVE_USERS.count(message.from_user.id)

    await message.reply_text(
        f"ℹ️ **Queue Status**\n\n🔵 **Total Queued Tasks:** {len(ACTIVE_USERS) - x}\n\n🟢 **Total Active Tasks:** {x}\n\n⏰ **Your Tasks:** {y}"
    )


# Owner Commands


@app.on_message(
    filters.command("restart")
    & filters.private
    & filters.incoming
    & filters.user(OWNER_ID)
)
async def restart(client: Client, message: Message):
    global ACTIVE_USERS

    for user_id in ACTIVE_USERS:
        try:
            await client.send_message(
                user_id,
                "♻️ **Bot Restarting Now**\n\nDue to recent updates to the code, the bot is restarting.\n\nYou will need to send /convert again to initiate the process.",
            )
        except Exception as e:
            print(e)

    await message.reply_text(f"♻️ **Message sent to {len(ACTIVE_USERS)} users**")


@app.on_message(
    filters.command("logs")
    & filters.private
    & filters.incoming
    & filters.user(OWNER_ID)
)
async def logs(client: Client, message: Message):
    await message.reply_document("logs.txt")


async def main():
    logger.info("Cleaning File Cache")
    reset_directory()

    logger.info("Starting Queue Handler")
    asyncio.create_task(queue_handler())

    logger.info("Starting Log Updater")
    asyncio.create_task(log_updater(logger_bot))

    logger.info("Starting PlayerX Stream Updater")
    asyncio.create_task(playerxstream_updater())

    await start_clients()
    await idle()


loop = asyncio.get_event_loop()


if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(err)
    finally:
        loop.stop()
        print("Bot Stopped!")
