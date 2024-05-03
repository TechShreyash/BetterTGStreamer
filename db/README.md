## Mongo DB API For Better TG Streamer

The Mongo DB API facilitates data retrieval and management for the Better TG Streamer, ensuring efficient operations necessary for stream management and user interactions.

### Setup

- **Configure MongoDB URL**: Update the `MONGO_DB_URL` in `main.py` to connect your application to MongoDB. Ensure this URL matches the one used by the bot for consistent data access across your application.

### Deployment Guide for Flask App

#### Steps to Deploy

1. **Install Dependencies**: Run the following command to install all necessary Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**: Use Gunicorn to start your application, suitable for both development and production:
   ```bash
   gunicorn main:app
   ```

## Support Group

For inquiries or support, join our [Telegram Support Group](https://telegram.me/TechZBots_Support) or email [techshreyash123@gmail.com](mailto:techshreyash123@gmail.com).
