## Better TG Streamer API

The Better TG Streamer API is a Cloudflare Workers deployable m3u8 stream API designed for the Better TG Streamer bot. It includes an embedded video player that supports streaming with multiple qualities, multiple audio tracks, and multiple subtitles. This API provides fast streaming directly from Telegram, enhancing the user experience with seamless video playback.

**Demo**: [Stream API Homepage](https://stream.techzbots.co)  
**Demo Video**: [Sample Streaming Video](https://stream.techzbots.co/embed/KUEBFRGUML/master_c1.m3u8)

### Deploy to Cloudflare

Follow these steps to deploy the Better TG Streamer API on Cloudflare Workers:

1. **Install Wrangler CLI**: Download and install the Wrangler CLI tool from [Cloudflare's Developer Documentation](https://developers.cloudflare.com/workers/wrangler/install-and-update/).

2. **Login to Your Cloudflare Account**:  
   Use the following command to log in to your Cloudflare account through Wrangler:
   ```bash
   wrangler login
   ```

3. **Deploy to Cloudflare Workers**:  
   Once logged in, deploy your API to Cloudflare Workers using:
   ```bash
   wrangler deploy
   ```

### Support

If you encounter any issues or require assistance, please join our [Telegram Support Group](https://telegram.me/TechZBots_Support) or send an email to [techshreyash123@gmail.com](mailto:techshreyash123@gmail.com).