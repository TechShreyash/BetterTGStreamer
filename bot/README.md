# Better TG Streamer Bot

**Better TG Streamer Bot** is a Telegram bot that manages the conversion of videos to m3u8 format.

**Demo Bot**: [BetterTGStreamerBot](https://telegram.me/BetterTGStreamerBot)

## Features

- Converts video files to m3u8 format quickly while preserving the original quality, including multiple audio tracks.
- Encodes video to m3u8 format with options for multiple quality levels, audio tracks, and subtitles using H.264/AAC.
- Supports uploading files from remote URLs for encoding.
- Displays the status of current and queued tasks.

## Commands

- `/start` - Retrieve bot information.
- `/help` - Instructions on how to use the bot.
- `/convert` - Convert a video to m3u8 format, maintaining original quality with support for multiple audio tracks.
- `/encode` - Encode a video to m3u8 format with multiple quality options, audio tracks, and subtitles.
- `/remote` - Upload a file from a remote URL for encoding.
- `/queue` - Check the status of processing and queued tasks.

## Deployment Guide

### Pre-requisites

- Ensure Docker is installed on your system.

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

- **Docker**: For deploying on a VPS using Docker, refer to the [Scripts Folder](./scripts).

## Configuration Variables

### Required Variables

- **API_ID**: The Telegram API ID necessary for interaction with the Telegram API.
- **API_HASH**: The Telegram API Hash corresponding to the API_ID, used for authentication.
- **VIDEO_STORAGE**: Telegram Channel ID where videos are stored.
- **LOGGER_CHANNEL**: Telegram Channel ID where logs are stored.
- **STORAGE_CHANNEL_1**: Telegram Channel ID where the m3u8 files for one set of content are stored.
- **OWNER_ID**: Telegram User ID of the bot owner, used for administrative purposes.
- **WEBSITE_DOMAIN**: The domain name where the streaming API is hosted, enabling stream management.
- **MONGO_DB_URL**: Connection string for MongoDB, used for data persistence across bot sessions.
- **PLAYERX_EMAIL**: Email used for logging into Playerx.stream.
- **PLAYERX_PASSWORD**: Password for Playerx.stream account.
- **PLAYERX_API_KEY**: API key for accessing Playerx.stream functionalities.

### Bot Token Variables

- **MAIN_BOT_TOKEN**: Handles user commands and interactions with the main bot.
- **LOGGER_BOT_TOKEN**: Sends log updates to the `LOGGER_CHANNEL`.
- **UPLOADER_BOTS_1**: Manages the upload of m3u8 files to `STORAGE_CHANNEL_1`.

### Optional Variables

- **UPLOADER_BOTS_2**: Additional bot tokens used for managing uploads to a secondary storage channel.
- **STORAGE_CHANNEL_2**: A secondary Telegram Channel ID used for storing additional m3u8 files.
- **MAX_ACTIVE_TASKS**: The maximum number of tasks that can run simultaneously on the system.
- **MAX_USER_CONCURRENT_TASKS**: The maximum number of concurrent tasks a single user can initiate.
- **SEGMENT_SIZE**: Specifies the size, in MB, of each segment uploaded to Telegram, ensuring it does not exceed platform limits.

## FAQs / Useful Information

**Why are multiple bot tokens added to UPLOADER_BOTS_1 and UPLOADER_BOTS_2?**

- Utilizing multiple bot tokens helps distribute the workload across various bots, significantly reducing the chances of receiving floodwait errors from Telegram's API. These errors typically occur when a bot tries to upload or download a large number of .ts files within a short period.

**Why are there two channels, STORAGE_CHANNEL_1 and STORAGE_CHANNEL_2?**

- Each Telegram channel can have a maximum of 50 admins. If you need to employ more bots to manage uploads, utilizing two channels is necessary. This setup allows you to have up to 100 bots (50 per channel) working simultaneously, enhancing efficiency and capacity.

Additional information will be added as questions arise from users. Contact info given below.

## Support Group

For inquiries or support, join our [Telegram Support Group](https://telegram.me/TechZBots_Support) or email [techshreyash123@gmail.com](mailto:techshreyash123@gmail.com).
