import cv2
import gi
import numpy as np

gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

pipeline_description = """
udpsrc port=5000 ! tsdemux name=demux \
demux. ! multiqueue name=mq ! video/x-h264 ! decodebin ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink
demux. ! mq. mq. ! meta/x-klv ! appsink name=klv_sink
"""

# GStreamer pipeline
pipeline = Gst.parse_launch(pipeline_description)

# Get the appsink element
video_sink = pipeline.get_by_name("sink")
# klv_sink = pipeline.get_by_name("klv_sink")
# Configure appsink properties
video_sink.set_property("emit-signals", False)  # Disable signals for pull mode
video_sink.set_property("drop", True)          # Drop old frames if queue is full

# klv_sink.set_property("emit-signals", False)  # Disable signals for pull mode
# klv_sink.set_property("drop", True) 

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

try:
    while True:
        # Pull a sample from appsink
        print("eee")
        sample = video_sink.emit("pull-sample")
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
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        print("111")
        # Unmap the buffer
        buffer.unmap(map_info)

except KeyboardInterrupt:
    print("Stopping...")

# Clean up
pipeline.set_state(Gst.State.NULL)
cv2.destroyAllWindows()
