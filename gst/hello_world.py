"""simple pipeline and wait for bus message

Tags:
    - add_signal_watch
    - bus
    - pipeline
        - set_state
        - get_bus
"""
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

PIPELINE = "videotestsrc ! videoconvert ! fpsdisplaysink"

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
    elif message.type == Gst.MessageType.STATE_CHANGED:
        old, new, pending = message.parse_state_changed()
        print(f"State changed from {old.value_name} to {new.value_name}")
    return True

pipeline = Gst.parse_launch(PIPELINE)

pipeline.set_state(Gst.State.PLAYING)

bus = pipeline.get_bus()
bus.add_signal_watch()
loop = GLib.MainLoop()
bus.connect("message", bus_callback, loop)
try:
    loop.run()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    pipeline.set_state(Gst.State.NULL)