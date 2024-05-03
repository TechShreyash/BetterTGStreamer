import asyncio, time
import subprocess, os, cv2
from config import SEGMENT_SIZE
from utils.Logger import Logger

logger = Logger(__name__)


def get_byterate(file_path):
    try:
        file_size = os.path.getsize(file_path)

        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        byte_rate = file_size / duration
        return byte_rate
    except Exception as e:
        logger.error(f"Error in getting bitrate : {e}")
        raise Exception(f"Error in getting bitrate : {e}")


async def transcode_video(input_file, output_file, hash, proc):
    await asyncio.sleep(5)
    logger.info(f"Transcoding {hash}")
    try:
        await proc.edit("🧿 **Transcoding started...**")
    except Exception as e:
        logger.warning(e)

    await asyncio.sleep(1)

    try:
        video_bitrate = get_byterate(input_file)  # in Bytes
        if video_bitrate != 0:
            hls_time = round(
                (SEGMENT_SIZE * 1024 * 1024) / (video_bitrate)
            )  # to make near 5 mb size of each ts file

            if hls_time > 30:
                hls_time = 30
            if hls_time < 5:
                hls_time = 5
        else:
            raise Exception("Error in getting video bitrate")

        # Construct the FFmpeg command
        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            input_file,
            "-c",
            "copy",
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-map",
            "0:s*?",
            "-start_number",
            "0",
            "-fs",
            "10M",
            "-hls_time",
            str(hls_time),
            "-hls_list_size",
            "0",
            "-f",
            "hls",
            output_file,
        ]

        # Execute the FFmpeg command
        process = subprocess.Popen(
            ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Monitor progress
        t1 = time.time()

        while True:
            line = process.stderr.readline().decode("utf-8")
            if not line:
                break

            if "Opening" in line:
                if ".ts" in line:
                    t2 = time.time()
                    if (t2 - t1) > 10:
                        try:
                            a = line.find("index")
                            b = line.find(".ts")
                            files_done = line[a + 5 : b]
                            text = f"🧿 **Transcoding : {files_done} files generated**"
                            await proc.edit(text)
                            t1 = time.time()
                        except Exception as e:
                            logger.warning(e)

        # Wait for the process to finish
        process.communicate()
        if process.returncode != 0:
            error = process.stderr.read().decode("utf-8")
            raise Exception(f"Transcoding failed : {error}")
    except Exception as e:
        logger.error(f"Error in transcoder : {e}")
        return False, e

    await asyncio.sleep(5)

    logger.info(f"Transcoding Complete {hash}")
    try:
        await proc.edit("🧿 **Transcoding Completed**")
    except Exception as e:
        logger.warning(e)
    return True, None