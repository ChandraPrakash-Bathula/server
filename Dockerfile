# Use official Python base
FROM python:3.11-slim

# Install FFMPEG
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn with 2 workers, 120s timeout
CMD ["gunicorn", "-w", "2", "-t", "120", "-b", "0.0.0.0:5000", "app:app"]
