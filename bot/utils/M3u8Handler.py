import asyncio, aiohttp, m3u8
from pyrogram.types import Message
from config import WEBSITE_DOMAIN
from utils.Database import save_file
from utils.Logger import Logger
from utils.Uploader import Multi_TS_DL_And_Uploader, Multi_TS_File_Uploader, send_file
from pyrogram.errors import FloodWait
from typing import Literal

logger = Logger(__name__)


async def Single_M3U8_Uploader(
    session: aiohttp.ClientSession, proc: Message, m3u8: str, hash: str
):
    await asyncio.sleep(5)

    try:
        await proc.edit(
            "📤 **Uploading File To Telegram...**\n\n⚠️ **Note :** If the file is too large, it may take some time to upload all files. Please be patient."
        )
    except Exception as e:
        logger.warning(e)

    logger.info(f"Uploading File {hash}")
    await asyncio.sleep(1)

    dir = "/".join(m3u8.split("/")[:-1])

    with open(m3u8, "r") as f:
        m3u8_file_text = f.read()

    tsFiles = []

    for line in m3u8_file_text.splitlines():
        line = line.strip()
        if line.endswith(".ts"):
            line = line.strip()
            tsFiles.append(line)

    for i in range(len(tsFiles)):
        tsFiles[i] = dir + "/" + tsFiles[i]

    tsData, new_file_list = await Multi_TS_File_Uploader(session, tsFiles, proc, hash)

    for i, k in new_file_list:
        m3u8_file_text = m3u8_file_text.replace(i, k)

    err_count = 0
    while True:
        if err_count == 5:
            raise Exception("Failed to upload ts file...")
        try:
            msg, channel = await send_file(session, m3u8_file_text.encode(), True)
            tsData[f"index_c{channel}.m3u8"] = msg["message_id"]
            break
        except FloodWait as e:
            logger.error(f"FloodWait Error : {e}")
            try:
                await proc.edit(
                    f"⚠️ **FloodWait Error :** Sleeping for {e.value} seconds"
                )
            except Exception as e:
                logger.warning(e)

            await asyncio.sleep(e.value)
            continue
        except Exception as e:
            err_count += 1
            logger.error(f"Error while uploading ts file {e}")

    try:
        await proc.edit("📤 **Uploaded Successfully**")
    except Exception as e:
        logger.warning(e)

    logger.info(f"Uploaded Successfully {hash}")

    await save_file(hash, tsData)
    logger.info(f"Saved to Database {hash}")
    await asyncio.sleep(5)
    return f"index_c{channel}.m3u8"


async def Multi_M3U8_Uploader(
    session: aiohttp.ClientSession,
    proc: Message,
    m3u8_url: str,
    headers: dict,
    hash: str,
    name: str,
    master_m3u8_text: str,
    _type: Literal["video", "audio"],
):
    await asyncio.sleep(5)
    async with session.get(m3u8_url, headers=headers) as r:
        m3u8_file_text = await r.text()

    m3u8_obj = m3u8.loads(m3u8_file_text)
    pos = 0
    file_list = []

    for segment in m3u8_obj.segments:
        pos += 1
        file_url = segment.uri
        ts_name = f"{hash}_part{pos}.ts"

        file_list.append((ts_name, file_url))

    try:
        tsData, file_list = await Multi_TS_DL_And_Uploader(
            session, file_list, proc, hash, name, headers
        )
    except Exception as e:
        # Handle if one quality fails
        try:
            await proc.edit(f"❌ **Failed To Upload {name} :** {e}")
        except Exception as e:
            logger.warning(e)

        await asyncio.sleep(5)

        item_to_be_removed = m3u8_url.split("/")[-1]
        lines = master_m3u8_text.splitlines()
        item_pos = 0

        for pos in range(len(lines)):
            line = lines[pos].strip()
            if item_to_be_removed == line:
                item_pos = pos
                break

        master_m3u8_text = "\n".join(lines[: item_pos - 1] + lines[item_pos + 1 :])
        return {}, master_m3u8_text

    for name, url in file_list:
        m3u8_file_text = m3u8_file_text.replace(url, name)

    await asyncio.sleep(1)

    err_count = 0
    while True:
        if err_count == 5:
            raise Exception("Failed to upload ts file...")
        try:
            msg, channel = await send_file(session, m3u8_file_text.encode(), True)
            tsData[f"{hash}_c{channel}.m3u8"] = msg["message_id"]
            if _type == "video":
                master_m3u8_text = master_m3u8_text.replace(
                    m3u8_url.split("/")[-1], f"{hash}_c{channel}.m3u8"
                )
            if _type == "audio":
                master_m3u8_text = master_m3u8_text.replace(
                    "/".join(m3u8_url.split("/")[-3:]), f"{hash}_c{channel}.m3u8"
                )
            break
        except FloodWait as e:
            logger.error(f"FloodWait Error : {e}")
            try:
                await proc.edit(
                    f"⚠️ **FloodWait Error :** Sleeping for {e.value} seconds"
                )
            except Exception as e:
                logger.warning(e)

            await asyncio.sleep(e.value)
            continue
        except Exception as e:
            err_count += 1
            logger.error(f"Error while uploading ts file {e}")

    await asyncio.sleep(5)
    return tsData, master_m3u8_text


async def Video_Handler(
    session: aiohttp.ClientSession,
    proc: Message,
    data: dict,
    headers: dict,
    hash: str,
    master_m3u8_text,
):
    combined_video_data = {}
    await asyncio.sleep(1)

    for q, url in data["video_url"]:
        logger.info(f"Uploading {q}p Quality Video To Telegram...")
        try:
            await proc.edit(f"📤 **Uploading {q}p Quality Video To Telegram...**")
        except Exception as e:
            logger.warning(e)
        await asyncio.sleep(1)

        tsData, master_m3u8_text = await Multi_M3U8_Uploader(
            session,
            proc,
            url,
            headers,
            f"{hash}_{q}p",
            f"{q}p Video",
            master_m3u8_text,
            "video",
        )
        combined_video_data.update(tsData)

        logger.info(f"Uploaded {q}p Quality Video To Telegram...")
        try:
            await proc.edit(f"📤 **Uploaded {q}p Quality Video To Telegram...**")
        except Exception as e:
            logger.warning(e)
        await asyncio.sleep(1)

    return combined_video_data, master_m3u8_text


async def Audio_Handler(
    session: aiohttp.ClientSession,
    proc: Message,
    data: dict,
    headers: dict,
    hash: str,
    master_m3u8_text: str,
):
    combined_audio_data = {}
    await asyncio.sleep(1)
    pos = 0

    for t, url in data["audio_url"]:
        pos += 1

        logger.info(f"Uploading Audio {pos} ({t}) To Telegram...")
        try:
            await proc.edit(f"📤 **Uploading Audio {pos} ({t}) To Telegram...**")
        except Exception as e:
            logger.warning(e)
        await asyncio.sleep(1)

        tsData, master_m3u8_text = await Multi_M3U8_Uploader(
            session,
            proc,
            url,
            headers,
            f"{hash}_audio_{pos}",
            f"Audio {pos} ({t})",
            master_m3u8_text,
            "audio",
        )
        combined_audio_data.update(tsData)

        logger.info(f"Uploaded Audio {pos} ({t}) To Telegram...")
        try:
            await proc.edit(f"📤 **Uploaded Audio {pos} ({t}) To Telegram...**")
        except Exception as e:
            logger.warning(e)
        await asyncio.sleep(1)

    return combined_audio_data, master_m3u8_text


async def Subtitle_Handler(
    session: aiohttp.ClientSession,
    proc: Message,
    data: dict,
    headers: dict,
    hash: str,
):
    await asyncio.sleep(5)
    total_files = len(data["subtitle_url"])
    if total_files == 0:
        return {}, "", {}

    combined_subtitle_data = {}
    await asyncio.sleep(1)
    pos = 0
    subtile_text = "🗒 **Subtitle Files :**\n\n"
    subtitle_data = {}

    for t, url in data["subtitle_url"]:
        pos += 1

        logger.info(f"Uploading subtitle_{pos} ({t}) To Telegram...")
        try:
            await proc.edit(f"📤 **Uploading Subtitle {pos} ({t}) To Telegram...**")
        except Exception as e:
            logger.warning(e)
        await asyncio.sleep(1)

        async with session.get(url, headers=headers) as r:
            if r.status != 200:
                raise Exception("Failed To Download Video Segment")

            bytes_data = await r.read()

            file_size = int(r.headers.get("Content-Length", 0))
            if file_size == 0:
                file_size = len(bytes_data)

            if file_size > (19.5 * 1024 * 1024):
                raise Exception("Too High Video Bitrate")

            err_count = 0
            while True:
                if err_count == 5:
                    raise Exception("Failed to upload ts file...")
                try:
                    msg, channel = await send_file(session, bytes_data, True)
                    combined_subtitle_data[f"subtitle_{pos}_c{channel}.srt"] = msg[
                        "message_id"
                    ]
                    subtile_text += f"🔹 Subtitle {pos} ({t}) : {WEBSITE_DOMAIN}/file/{hash}/subtitle_{pos}_c{channel}.srt \n"
                    await asyncio.sleep(1)
                    break
                except FloodWait as e:
                    logger.error(f"FloodWait Error : {e}")
                    try:
                        await proc.edit(
                            f"⚠️ **FloodWait Error :** Sleeping for {e.value} seconds"
                        )
                    except Exception as e:
                        logger.warning(e)

                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    err_count += 1
                    logger.error(f"Error while uploading ts file {e}")

        subtitle_data[t] = f"subtitle_{pos}_c{channel}.srt"

    await asyncio.sleep(5)
    return combined_subtitle_data, subtile_text, subtitle_data


async def Master_Handler(
    session: aiohttp.ClientSession, proc: Message, data: dict, headers: dict, hash: str
):
    await asyncio.sleep(5)
    try:
        await proc.edit("🔄 **Extracting Video URLs And Data...**")
    except:
        pass
    await asyncio.sleep(1)

    master_m3u8_text, data = await Master_Extractor(session, data, headers)
    master_data = {}

    # Upload Video Files
    combined_video_data, master_m3u8_text = await Video_Handler(
        session, proc, data, headers, hash, master_m3u8_text
    )
    master_data.update(combined_video_data)

    # Upload Audio Files
    combined_audio_data, master_m3u8_text = await Audio_Handler(
        session, proc, data, headers, hash, master_m3u8_text
    )
    master_data.update(combined_audio_data)

    # Upload Subtitle Files
    combined_subtitle_data, subtile_text, subtitle_data = await Subtitle_Handler(
        session, proc, data, headers, hash
    )
    master_data.update(combined_subtitle_data)

    # Upload Master M3U8 File
    await asyncio.sleep(1)
    err_count = 0
    while True:
        if err_count == 5:
            raise Exception("Failed to upload ts file...")
        try:
            msg, channel = await send_file(session, master_m3u8_text.encode(), True)
            m3u8 = f"master_c{channel}.m3u8"
            master_data[m3u8] = msg["message_id"]
            break
        except FloodWait as e:
            logger.error(f"FloodWait Error : {e}")
            try:
                await proc.edit(
                    f"⚠️ **FloodWait Error :** Sleeping for {e.value} seconds"
                )
            except Exception as e:
                logger.warning(e)

            await asyncio.sleep(e.value)
            continue
        except Exception as e:
            err_count += 1
            logger.error(f"Error while uploading ts file {e}")

    await asyncio.sleep(1)
    try:
        await proc.edit("📤 **Uploaded Master M3U8 File To Telegram...**")
    except Exception as e:
        logger.warning(e)

    await asyncio.sleep(1)

    await save_file(hash, master_data, subtitle_data)
    logger.info(f"Saved to Database {hash}")
    await asyncio.sleep(5)

    return subtile_text, m3u8


async def Master_Extractor(session: aiohttp.ClientSession, data: dict, headers: dict):
    master_url = data["video_url"]
    async with session.get(master_url, headers=headers) as r:
        content = await r.text()

    master_m3u8_text = content

    m3u8_obj = m3u8.loads(content)
    path = "/".join(master_url.split("/")[:-1])
    qualities = []

    for quality in m3u8_obj.playlists:
        qualities.append((quality.stream_info.resolution[1], path + "/" + quality.uri))

    audios = []
    for i in m3u8_obj.media:
        lang = (i.language or "Unknown").upper()
        name = i.name
        audios.append((f"{lang} - {name}", path + "/" + i.uri))

    data["video_url"] = qualities
    data["audio_url"] = audios
    data["subtitle_url"] = data.pop("video_subtitle")

    return master_m3u8_text, data
