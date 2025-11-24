FROM python:3.11-slim

# Install ffmpeg for audio extraction and other media processing
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install latest yt-dlp instead of specific version
RUN pip install --no-cache-dir Flask==3.0.0 requests packaging && \
    pip install --no-cache-dir --upgrade yt-dlp

# Copy application files
COPY app.py .
COPY templates/ templates/

# Create downloads and logs directories
RUN mkdir -p /downloads /app/logs && chmod 777 /app/logs

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
