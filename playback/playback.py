import os
import time
import logging
from obspy import read
import python_libmseed

# Constants
RING_DIR = "/ringserver/ring"
MINISEED_FILE = os.getenv("MSEED_FILE", "test.mseed")
MINISEED_PATH = f"/mseed_files/{MINISEED_FILE}"

RECORD_SIZE = 512      # MiniSEED fixed record size in bytes
HEADER_SIZE = 48       # Approximate MiniSEED fixed header size (bytes)
PAYLOAD_SIZE = RECORD_SIZE - HEADER_SIZE

# Setup logger
logger = logging.getLogger("ring_playback")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def samples_per_record(bytes_per_sample):
    """Calculate how many samples fit in the payload area of a record."""
    return PAYLOAD_SIZE // bytes_per_sample

def encode_record(tr, data_chunk, seq_num):
    """Create and encode a MiniSEED record from data chunk."""
    record = python_libmseed.MSeedRecord()
    record.network = tr.stats.network
    record.station = tr.stats.station
    record.channel = tr.stats.channel
    record.location = tr.stats.location if "location" in tr.stats else ""
    # Calculate start time offset for this chunk (seconds)
    record.starttime = tr.stats.starttime.timestamp + (seq_num * len(data_chunk)) / tr.stats.sampling_rate
    record.sr = tr.stats.sampling_rate
    record.samples = list(data_chunk)
    record.sequence_number = seq_num
    record.encoding = python_libmseed.MSEED_ENC_INT32  # adjust if needed
    record.record_length = RECORD_SIZE
    return record.encode()

def playback(miniseed_path, ring_dir):
    logger.info(f"Reading MiniSEED file: {miniseed_path}")
    stream = read(miniseed_path)
    logger.info(f"Opening ring buffer at: {ring_dir}")
    ring = python_libmseed.ringbuffer_open(ring_dir, flags=python_libmseed.RINGBUF_WRITE)

    trace_chunks = []
    for tr in stream:
        bytes_per_sample = tr.data.itemsize
        n_samples = samples_per_record(bytes_per_sample)
        data = tr.data
        chunks = [data[i:i+n_samples] for i in range(0, len(data), n_samples)]
        trace_chunks.append({
            "trace": tr,
            "chunks": chunks,
            "seq": 0
        })
        logger.info(f"Prepared {len(chunks)} chunks for trace {tr.id} (samples per chunk: {n_samples})")

    max_chunks = max(len(tc["chunks"]) for tc in trace_chunks)
    logger.info(f"Starting playback of {max_chunks} chunk rounds")

    for chunk_idx in range(max_chunks):
        for tc in trace_chunks:
            if chunk_idx >= len(tc["chunks"]):
                continue
            tr = tc["trace"]
            chunk = tc["chunks"][chunk_idx]
            seq = tc["seq"]
            try:
                record_bytes = encode_record(tr, chunk, seq)
                python_libmseed.ringbuffer_write(ring, record_bytes)
                logger.info(f"Wrote chunk {seq} for trace {tr.id} ({len(chunk)} samples)")
            except Exception as e:
                logger.error(f"Error encoding/writing record for trace {tr.id} chunk {seq}: {e}")
                continue
            tc["seq"] += 1

            duration = len(chunk) / tr.stats.sampling_rate
            time.sleep(duration * 0.95)  # slight speed-up

    python_libmseed.ringbuffer_close(ring)
    logger.info("Playback finished, ring buffer closed.")

if __name__ == "__main__":
    logger.info(f"Starting playback of {MINISEED_PATH} into ring {RING_DIR}")
    playback(MINISEED_PATH, RING_DIR)
