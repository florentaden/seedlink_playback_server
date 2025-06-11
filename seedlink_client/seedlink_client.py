from obspy.clients.seedlink.easyseedlink import EasySeedLinkClient

# Subclass the client class
class MyClient(EasySeedLinkClient):
    # Implement the on_data callback
    def on_data(self, trace):
        print("=== Received trace ===")
        starttime = trace.stats.starttime
        endtime = trace.stats.endtime
        print(f"[{trace.stats.starttime}] Received {trace.id} with {len(trace.data)} samples ({starttime}-{endtime})")

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

