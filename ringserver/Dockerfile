FROM debian:bullseye

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libglib2.0-dev \
    libmseed-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone and build ringserver
RUN git clone https://github.com/iris-edu/ringserver.git /opt/ringserver \
    && cd /opt/ringserver \
    && make \
    && make install

# Create working directory
RUN mkdir -p /ringserver/ring

# Default config and port
WORKDIR /ringserver

# Expose SeedLink port
EXPOSE 18000

# Start the ringserver
# ENTRYPOINT ["/opt/ringserver/ringserver", "-v", "-Rd", "/ringserver/ring", "-Rs", "100000000", "-L", "18000"]
