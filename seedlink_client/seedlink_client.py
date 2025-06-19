from obspy.clients.seedlink.easyseedlink import EasySeedLinkClient
from obspy import Stream, UTCDateTime
import time
import os 
import traceback

PLOT_DIR = "/plots"

# Subclass the client class
class MyClient(EasySeedLinkClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = Stream()
        self.last_plot_time = time.time()
        os.makedirs(PLOT_DIR, exist_ok=True)
        
    # callback when data is received
    def on_data(self, trace):
        print(f"Received Trace: {trace.id} | Start: {trace.stats.starttime} | Samples: {len(trace.data)}")
        self.stream += trace
        self.stream.merge(method=1, fill_value=0)
        print(self.stream)

        if time.time() - self.last_plot_time > 2:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            plot_path = os.path.join(PLOT_DIR, f"latest_waveforms.png")
            try:
                self.stream.plot(
                    outfile=plot_path,
                    size=(1200, 200*len(self.stream)),
                    equal_scale=False,
                    starttime=UTCDateTime() - 300,
                    endtime=UTCDateTime(),
                    )
                print(f"Saved plot to {plot_path}")
            except Exception as e:
                # print(f"Failed to save plot: {e}")
                print(traceback.format_exc())
            # self.stream = Stream()  # Reset
            self.last_plot_time = time.time()

# Connect to a SeedLink server
client = MyClient('ringserver:18000')
print("=== Client Connected ===")

# Retrieve INFO:STREAMS
streams_xml = client.get_info('STREAMS')
print("=== Available STREAMS ===")
print(streams_xml)
print(client.get_info('ALL'))

# Select a stream and start receiving data
client.select_stream('NZ', 'WEL', 'HHZ')
client.select_stream('IU', 'SNZO', 'HHZ')
client.run()

