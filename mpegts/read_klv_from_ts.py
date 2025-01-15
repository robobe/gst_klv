# ffmpeg -i output.ts -map 0:1 -c copy -f metadata.bin
#  gst-launch-1.0 filesrc location=output_klv.ts ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! autovideosink
# gst-launch-1.0 filesrc location=output_klv.ts !  ! fakesink
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)
# Create the GStreamer pipeline

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

pipeline_str = """
filesrc location=data/output_klv.ts ! tsdemux name=demux 
demux. ! queue ! meta/x-klv ! appsink name=klv_sink
"""

pipeline = Gst.parse_launch(pipeline_str)
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

# Start the pipeline
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