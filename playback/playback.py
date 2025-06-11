import os
import time
import logging
import numpy as np
import traceback
from obspy import read, UTCDateTime, Stream
from typing import Optional

# Constants
TARGET_PATH = "/data/miniseed"
MINISEED_FILE = os.getenv("MSEED_FILE")
INPUT_MINISEED_PATH = f"/mseed_files/{MINISEED_FILE}"

# Logger
logger = logging.getLogger("playback")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def write_mseed_chunks(
    stream: Stream,
    target_dir: str,
    record_length: int = 512,
    chunk_duration: float = 5.,
    start_offset: float = 5.,
    delete_older_than: float = 3600.):
    """
    Simulates real-time streaming by writing miniSEED files per time slice.

    Parameters
    ----------
    stream : obspy.Stream
        Input stream containing multiple traces.
    target_dir : str
        Directory where output files will be written.
    record_length : int
        MiniSEED record length (e.g., 512).
    chunk_duration : float
        Time slice duration in seconds (default is 5s).
    start_offset : float
        Time offset relative to now to start playback (default is 5s).
    delete_older_than : float or None
        Seconds after which old files should be deleted (default is 3600s).
    """
    # Step 1: Align start times to simulate "now + offset seconds"
    t0 = UTCDateTime() + start_offset
    time_shift = t0 - min(tr.stats.starttime for tr in stream)
    for tr in stream:
        tr.stats.starttime += time_shift

    # Step 2: Define global playback time range
    tmax = max(tr.stats.endtime for tr in stream)
    n_slices = int((tmax - t0) / chunk_duration) + 1

    for i in range(n_slices):
        slice_start = t0 + i * chunk_duration
        slice_end = t0 + (i + 1) * chunk_duration

        # Step 3: Slice all traces for this time window
        chunk_stream = stream.slice(slice_start, slice_end, nearest_sample=False)
        if len(chunk_stream) == 0 or all(len(tr.data) == 0 for tr in chunk_stream):
            continue  # Skip empty slices

        # Step 4: Write as a single file
        ts_tag = slice_start.format_iris_web_service().replace(":", "").replace("-", "")
        fname = f"slice_{ts_tag}.mseed"
        chunk_path = os.path.join(target_dir, fname)
        
        chunk_stream.write(chunk_path, format="MSEED", reclen=record_length)
        logger.info(f"Wrote {chunk_path}  ({len(chunk_stream)} traces)")

        # Step 5: delete old files
        cutoff = time.time() - delete_older_than
        for fn in os.listdir(target_dir):
            if not fn.endswith(".mseed"):
                continue
            fpath = os.path.join(target_dir, fn)
            try:
                if os.stat(fpath).st_mtime < cutoff:
                    os.remove(fpath)
                    logger.debug(f"Deleted {fpath}")
            except Exception:
                pass

        # Step 6: Real-time pacing
        time.sleep(chunk_duration * 0.95)


if __name__ == "__main__":
    logger.info(f"Reading MiniSEED file: {INPUT_MINISEED_PATH}")
    stream = read(INPUT_MINISEED_PATH)
    write_mseed_chunks(stream, TARGET_PATH)