# Use a slim Python image for smaller size
FROM python:3.10-slim

# Install system dependencies and netcat for wait-for-port (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libmseed-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone and install mseedlib
RUN git clone https://github.com/EarthScope/mseedlib.git /mseedlib \
    && pip install /mseedlib

# Install python packages
RUN pip install --no-cache-dir obspy

# Create app directory
WORKDIR /app

# Copy your playback script into the container
COPY playback.py /app/playback.py

# Run playback directly
# ENTRYPOINT ["python", "/app/playback.py"]
