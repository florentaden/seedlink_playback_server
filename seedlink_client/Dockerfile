# Use official Python base image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies for ObsPy (and any others needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install ObsPy (includes seedlink client)
RUN pip install --no-cache-dir obspy

# Copy your SeedLink client script into the container
COPY seedlink_client.py .

ENV PYTHONUNBUFFERED=1

# Run the script
# CMD ["python", "seedlink_client.py"]