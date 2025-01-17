"""simple pipeline and wait for bus message

Tags:
    - timed_pop_filtered
    - bus
"""
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

# Create a pipeline
pipeline = Gst.parse_launch("videotestsrc ! autovideosink")

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Get the bus
bus = pipeline.get_bus()

# Wait for an error or EOS for up to 10 seconds
message = bus.timed_pop_filtered(10 * Gst.SECOND, Gst.MessageType.ERROR | Gst.MessageType.EOS)

if message:
    if message.type == Gst.MessageType.EOS:
        print("End of Stream reached.")
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"Error occurred: {err.message}, {debug}")
else:
    print("No message received within the timeout.")

# Clean up
pipeline.set_state(Gst.State.NULL)
