import cv2
import gi
import numpy as np

gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

# GStreamer pipeline
pipeline = Gst.parse_launch(
    "videotestsrc ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink"
)

# Get the appsink element
appsink = pipeline.get_by_name("sink")

# Configure appsink properties
appsink.set_property("emit-signals", False)  # Disable signals for pull mode
appsink.set_property("drop", True)          # Drop old frames if queue is full

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

try:
    while True:
        # Pull a sample from appsink
        sample = appsink.emit("pull-sample")
        if not sample:
            print("End of stream or error")
            break

        # Get the buffer from the sample
        buffer = sample.get_buffer()
        success, map_info = buffer.map(Gst.MapFlags.READ)
        if not success:
            print("Failed to map buffer")
            continue

        # Extract raw video data
        frame_data = np.frombuffer(map_info.data, dtype=np.uint8)

        # Get video frame dimensions from the sample's caps
        caps = sample.get_caps()
        structure = caps.get_structure(0)
        width = structure.get_int("width")[1]
        height = structure.get_int("height")[1]

        # Reshape the data into an OpenCV image
        frame = frame_data.reshape((height, width, 3))

        # Display the frame using OpenCV
        cv2.imshow("GStreamer OpenCV", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Unmap the buffer
        buffer.unmap(map_info)

except KeyboardInterrupt:
    print("Stopping...")

# Clean up
pipeline.set_state(Gst.State.NULL)
cv2.destroyAllWindows()
