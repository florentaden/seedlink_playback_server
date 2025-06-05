import os
import time
import logging
import numpy as np
import traceback
from obspy import read, UTCDateTime
import mseedlib as msl

# Constants
TARGET_PATH = "/data/miniseed"
MINISEED_FILE = os.getenv("MSEED_FILE")
INPUT_MINISEED_PATH = f"/mseed_files/{MINISEED_FILE}"

# Logger
logger = logging.getLogger("playback")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def write_mseed_chunks(stream, target_dir, record_length=512, chunk_duration=5):
    for tr in stream:
        tr_start = UTCDateTime() + 5  # Delay playback start a little
        tr.stats.starttime = tr_start
        trace_id = tr.id.replace('.', '_')  # Safe filename

        # Break into smaller chunks if needed (to simulate real-time flow)
        chunk_samples = int(chunk_duration * tr.stats.sampling_rate)
        n_chunks = (len(tr.data) + chunk_samples - 1) // chunk_samples

        for i in range(n_chunks):
            chunk = tr.slice(
                starttime=tr.stats.starttime + i * chunk_duration,
                endtime=tr.stats.starttime + (i + 1) * chunk_duration
            )
            out_filename = f"{trace_id}_{i:04d}.mseed"
            out_path = os.path.join(target_dir, out_filename)

            if len(chunk) > 0:
                chunk.write(out_path, format="MSEED", reclen=record_length)
                logger.info(f"Wrote: {out_path}")
                time.sleep(chunk_duration * 0.95)  # Pacing to mimic real-time

if __name__ == "__main__":
    logger.info(f"Reading MiniSEED file: {INPUT_MINISEED_PATH}")
    stream = read(INPUT_MINISEED_PATH)
    write_mseed_chunks(stream, TARGET_PATH)