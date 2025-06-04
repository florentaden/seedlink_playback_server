from obspy.clients.seedlink.easyseedlink import EasySeedLinkClient

# Subclass the client class
class MyClient(EasySeedLinkClient):
    # Implement the on_data callback
    def on_data(self, trace):
        print("=== Received trace ===")
        print(trace)

# Connect to a SeedLink server
client = MyClient('ringserver:18000')

# Retrieve INFO:STREAMS
streams_xml = client.get_info('STREAMS')
print("=== Available STREAMS ===")
print(streams_xml)
print(client.get_info('ALL'))

# Select a stream and start receiving data
client.select_stream('NZ', 'WEL', 'HHZ')
client.run()