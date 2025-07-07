# Use Python slim as base image
FROM python:3.11-slim

# Install ffmpeg for video conversions
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Tell Docker how to run your app
CMD ["gunicorn", "-w", "2", "-t", "300", "-b", "0.0.0.0:5000", "app:app"]
