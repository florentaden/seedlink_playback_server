# 📡 Seedlink Playback Server

Simulate real-time playback of seismic miniSEED data into a [Ringserver](https://github.com/iris-edu/ringserver), enabling testing and development of SeedLink clients and processing pipelines.

This repository provides a Docker-based system to stream seismic data in chunks, mimicking live acquisition for educational, development, and testing purposes.

---

## 📦 Components

- **🔁 Ringserver**  
  A SeedLink server that serves seismic data from a watched directory using the SeedLink protocol.

- **⏯️ Playback Service**  
  Streams miniSEED files into the ringserver directory in timed chunks, simulating real-time data flow (using ObsPy).

- **📡 Client**  
  A simple SeedLink client (based on ObsPy) that connects to the ringserver, subscribes to data streams, prints incoming trace info and save plots of latest waveforms.

- **📈 Plot Viewer**  
  An optional service that renders incoming waveforms and serves them via a lightweight web interface.

---

## 🚀 Getting Started

## Getting Started with Docker Compose

### 1. ✅ Prerequisites

- <span class="checked">✔</span> Docker
- <span class="checked">✔</span> Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/florentaden/seedlink_playback_server.git
cd seedlink_playback_server
```

### 2. Use your miniSEED file 
Place a `.mseed` file inside the `mseed_files/` directory and edit the `docker-compose.yml` file at:
```env
environment:
      - MSEED_FILE=example.mseed
```

### 3. 📡 Launch the Docker stack
```bash
docker compose up --build
```

This will start:
- The ringserver on `localhost:18000`
- The playback container streaming the miniSEED file into the ringserver
- The client, which connects to the ringserver and logs incoming traces
- The plot viewer, which displays the latest waveforms received by the client

You should see logs from all three services in the terminal.
If you want to have the stack in background, you can add the flag `-d`.

### 4. 🖼️ Waveform Visualization
To view the latest waveforms being received:

- Open your browser and go to: http://localhost:8080
- The plot updates automatically every 5 seconds.

This is served using a lightweight Python HTTP server and an auto-refreshing HTML page.

### 5. 🔁 Volumes and Data

Docker volumes called `miniseed-data` and `plots` are used to pass the chunks of waveforms from the `playback` to the `ringserver` and figures from the `client` to the `web-server`
```yaml
volumes:
  miniseed-data:
    driver: local
  plots:
    driver: local
```

### 6. 🛑 Stopping the System

```bash
docker compose down
```

⚠️This will stop and remove containers and networks, but **volumes will be preserved**. Use this if you need/want to stop the system but keep the archives already computed as the data is stored in the docker volumes defined in the `docker-compose.yml` file.

To remove volumes as well (⚠️this deletes data!):
```bash
docker compose down --volumes
```


