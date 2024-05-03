# Use an official Python runtime as a parent image
FROM python:3.10

# Install FFmpeg and FFprobe
RUN apt-get update -qq && apt-get install -y ffmpeg

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps

# Run your Python script
CMD ["python", "main.py"]
