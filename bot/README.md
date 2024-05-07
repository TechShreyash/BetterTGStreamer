# Better TG Streamer Bot

**Better TG Streamer Bot** is a Telegram bot that facilitates video conversion to the m3u8 format.

**Demo Bot**: [BetterTGStreamerBot](https://telegram.me/BetterTGStreamerBot)

## Features

- Converts video files to m3u8 format quickly while preserving original quality and supporting multiple audio tracks.
- Offers multi-quality, multi-audio, and subtitle encoding using H.264/AAC.
- Allows uploads from remote URLs for encoding.
- Displays the status of current and queued tasks.

## Commands

- `/start` - Show bot information.
- `/help` - Provide usage instructions.
- `/convert` - Convert a video to m3u8 format, maintaining original quality with multiple audio tracks.
- `/encode` - Encode a video to m3u8 format with multiple quality options, audio tracks, and subtitles.
- `/remote` - Upload a file from a remote URL for encoding.
- `/queue` - Check the status of current and queued tasks.

[Read More](#bot-commands-and-their-functions) 

## Deployment Guide

### Prerequisites

- Docker installed on your system.

### Steps

1. Clone the repository and navigate to the `BetterTGStreamer/bot` directory.
2. Update the required configuration variables in `config.py`.
3. Build the application:
   ```bash
   docker build -t tgstreamer .
   ```
4. Run the application:
   ```bash
   docker run --name tgstreamer -d tgstreamer
   ```
   Monitor your bot’s activity via:
   ```bash
   docker logs -f tgstreamer
   ```

### Deployment Tips

- For VPS deployment with Docker, refer to the [Scripts Folder](./scripts).

## Configuration Variables

### Required Variables

- **API_ID**: Telegram API ID for interaction with the Telegram API.
- **API_HASH**: Telegram API hash corresponding to the API_ID for authentication.
- **VIDEO_STORAGE**: Telegram Channel ID for video storage.
- **LOGGER_CHANNEL**: Telegram Channel ID for logging.
- **STORAGE_CHANNEL_1**: Telegram Channel ID for storing m3u8 files.
- **OWNER_ID**: Telegram User ID of the bot owner.
- **WEBSITE_DOMAIN**: Domain name for streaming API hosting.
- **MONGO_DB_URL**: MongoDB connection string for data persistence.

### Bot Token Variables

- **MAIN_BOT_TOKEN**: Manages user commands and interactions.
- **LOGGER_BOT_TOKEN**: Sends log updates to `LOGGER_CHANNEL`.
- **UPLOADER_BOTS_1**: Manages uploads to `STORAGE_CHANNEL_1`.

### PlayerX Config

- **PLAYERX_EMAIL**: Playerx.stream account email.
- **PLAYERX_PASSWORD**: Playerx.stream account password.
- **PLAYERX_API_KEY**: Playerx.stream API key.

#### PlayerX Settings

- `Player Platform`: `VideoJS`
- `Auto Import GDrive`: `Enabled`
- `Multi Audio`: `Enabled`
- `Label Audio`: `Language`
- `Label Subtitle`: `Language`
- `Auto Import Subtitle`: `Enabled`
- `Encode Hardsub`: `Disabled`

Set all other settings to default.

### Optional Variables

- **UPLOADER_BOTS_2**: Additional bot tokens for a secondary storage channel.
- **STORAGE_CHANNEL_2**: Secondary Telegram Channel ID for m3u8 files.
- **MAX_ACTIVE_TASKS**: Maximum number of concurrent system tasks.
- **MAX_USER_CONCURRENT_TASKS**: Maximum concurrent tasks per user.
- **NO_OF_UPLOADERS**: Number of concurrent uploaders per task.
- **SEGMENT_SIZE**: Size in MB of each segment uploaded to Telegram.

## FAQs / Useful Information

### Bot Commands and Their Functions

- **/convert** (replied to a file): The bot downloads the specified file, converts it to m3u8 format using ffmpeg, and uploads the m3u8 and TS files to Telegram, storing the file IDs in MongoDB.

- **/encode** (replied to a file): The bot uploads the file to PlayerXstream, which encodes the video into multiple qualities with multiple audio tracks and subtitles in m3u8 format. The bot sends the PlayerXstream video link to the user.

- **/remote video_link**: The bot adds a video link from a remote host to PlayerXstream, which downloads and encodes the video. The bot provides the encoded video link to the user.

- **/convert playerx_video_link**: The bot downloads the m3u8, TS, and SRT files from PlayerXstream and uploads them to Telegram, saving the file IDs in the database.

- **/queue**: The bot operates on a queue system, adhering to maximum limits for total and per-user tasks. The `/queue` command displays the queue status, including the number of tasks queued and running, and the number of tasks added by the user.

### Using Multiple Bot Tokens

Utilizing multiple bot tokens distributes the workload across various bots, reducing the chances of receiving floodwait errors from Telegram's API when uploading or downloading large numbers of .ts files.

### Using Two Channels

Each Telegram channel can have a maximum of 50 admins. Utilizing two channels allows up to 100 bots (50 per channel) to work simultaneously, enhancing efficiency.

## Support Group

For inquiries or support, join our [Telegram Support Group](https://telegram.me/TechZBots_Support) or email [techshreyash123@gmail.com](mailto:techshreyash123@gmail.com).
