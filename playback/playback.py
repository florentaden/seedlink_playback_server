import os
import time
import logging
import numpy as np
import traceback
from obspy import read
import mseedlib as msl

# Constants
RING_PATH = "/ringserver/ring/packetbuf"
MINISEED_FILE = os.getenv("MSEED_FILE", "test.mseed")
MINISEED_PATH = f"/mseed_files/{MINISEED_FILE}"

RECORD_SIZE = 512  # miniSEED record length
HEADER_SIZE = 48   # approximate MiniSEED header size
PAYLOAD_SIZE = RECORD_SIZE - HEADER_SIZE
BYTES_PER_SAMPLE = 4  # assuming INT32 encoding

# Logger setup
logger = logging.getLogger("ring_playback")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

def playback(miniseed_path, ring_path):
    logger.info(f"Reading MiniSEED file: {miniseed_path}")
    stream = read(miniseed_path)

    logger.info(f"Opening ring buffer at: {ring_path}")
    ring_fd = os.open(ring_path, os.O_RDWR)

    samples_per_record = PAYLOAD_SIZE // BYTES_PER_SAMPLE

    # Pre-split all traces into chunks, store in a list of dicts
    trace_chunks = []
    for tr in stream:
        data_int = tr.data.astype(np.int32)
        total_samples = len(data_int)
        n_chunks = (total_samples + samples_per_record - 1) // samples_per_record

        # Compose sourceid string (FDSN format)
        location = tr.stats.location if tr.stats.location else "00"
        band, source, subsource = tr.stats.channel
        sourceid_base = f"FDSN:{tr.stats.network}_{tr.stats.station}_{location}_{band}_{source}_{subsource}"

        # Split data into chunks
        chunks = [data_int[i*samples_per_record : (i+1)*samples_per_record] for i in range(n_chunks)]

        trace_chunks.append({
            'trace': tr,
            'sourceid_base': sourceid_base,
            'chunks': chunks,
        })

        logger.info(f"Trace {tr.id} split into {n_chunks} chunks")

    max_chunks = max(len(tc['chunks']) for tc in trace_chunks)
    logger.info(f"Starting playback for {max_chunks} chunk rounds ({sourceid_base})")

    for chunk_idx in range(max_chunks):
        start_time = time.time()

        for tc in trace_chunks:
            if chunk_idx >= len(tc['chunks']):
                continue  # No chunk for this trace at this index, skip

            tr = tc['trace']
            sourceid_base = tc['sourceid_base']
            chunk = tc['chunks'][chunk_idx]

            # Calculate chunk start time in nanoseconds
            chunk_start_time_ns = int((tr.stats.starttime.timestamp + chunk_idx / tr.stats.sampling_rate) * 1_000_000_000)

            mstl = msl.MSTraceList()
            mstl.add_data(
                sourceid=sourceid_base,
                data_samples=chunk.tolist(),
                sample_type='i',
                sample_rate=tr.stats.sampling_rate,
                start_time=chunk_start_time_ns
            )

            def record_handler(record_bytes, handler_data):
                try:
                    os.write(handler_data['ring_fd'], record_bytes)
                except Exception as e:
                    logger.error(f"Failed to write record to ring buffer: {e}")
                    traceback.print_exc()

            mstl.pack(
                record_handler,
                {'ring_fd': ring_fd},
                format_version=3,
                record_length=RECORD_SIZE,
                flush_data=True
            )

            logger.info(f"Wrote chunk {chunk_idx + 1} for trace {tr.id} ({len(chunk)} samples)")

        # Sleep to pace streaming to real time chunk duration
        elapsed = time.time() - start_time
        chunk_duration = samples_per_record / stream[0].stats.sampling_rate
        sleep_time = max(0, chunk_duration - elapsed) * 0.95  # slightly less to keep up
        time.sleep(sleep_time)

    os.close(ring_fd)
    logger.info("Playback finished, ring buffer closed.")

if __name__ == "__main__":
    logger.info(f"Starting playback of {MINISEED_PATH} into ring {RING_PATH}")
    playback(MINISEED_PATH, RING_PATH)
