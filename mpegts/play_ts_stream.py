import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

def bus_callback(bus, message, loop):
    """
    Handle GStreamer bus messages.
    """
    if message.type == Gst.MessageType.EOS:
        print("End-of-stream received, exiting.")
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"Error: {err}, Debug Info: {debug}")
        loop.quit()
    return True

pipeline_description = """
udpsrc port=5000 ! tsdemux name=demux \
demux. ! multiqueue name=mq ! video/x-h264 ! decodebin ! videoconvert ! autovideosink
demux. ! mq. mq. ! meta/x-klv ! appsink name=klv_sink

"""
pipeline = Gst.parse_launch(pipeline_description)
appsink = pipeline.get_by_name("klv_sink")
counter = 0
def on_new_sample(sink):
    sample = appsink.emit('pull-sample')
    buffer = sample.get_buffer()
    success, mapinfo = buffer.map(Gst.MapFlags.READ)
    if success:
        # Here you can process the KLV data
        klv_data = mapinfo.data
        i = 0
        while i < len(klv_data):
            key = klv_data[i]
            length = klv_data[i + 1]
            value = klv_data[i + 2 : i + 2 + length]
            GLib.log_default_handler("MyApp", GLib.LogLevelFlags.LEVEL_MESSAGE, f"KLV Packet - Key: {key}, Length: {length}, Value: {value.hex()}")
            str_value = value.decode('utf-8')
            GLib.log_default_handler("MyApp", GLib.LogLevelFlags.LEVEL_MESSAGE, str_value)
            i += 2 + length
        buffer.unmap(mapinfo)
        
    return Gst.FlowReturn.OK



# Set the appsink properties
appsink.set_property("emit-signals", True)
appsink.connect("new-sample", on_new_sample)

pipeline.set_state(Gst.State.PLAYING)

bus = pipeline.get_bus()
bus.add_signal_watch()
loop = GLib.MainLoop()
bus.connect("message", bus_callback, loop)

try:
    print("Playing video with appsrc. Press Ctrl+C to stop.")
    loop.run()
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # Stop the pipeline
    
    pipeline.set_state(Gst.State.NULL)