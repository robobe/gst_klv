# 
# generate a simple video stream using appsrc and control video rate
import gi
import numpy as np
import cv2
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import time

# Initialize GStreamer
Gst.init(None)

# Create the GStreamer pipeline
pipeline_description = ("""appsrc name=source is-live=true  format=time \
    ! videoconvert \
    ! queue leaky=downstream max-size-buffers=1 \
    ! videorate name=rate \
    ! capsfilter name=capsfilter caps=video/x-raw,framerate=10/1 \
    ! videoconvert \
    ! queue \
    ! fpsdisplaysink sync=false"""
)
pipeline = Gst.parse_launch(pipeline_description)

# Get the appsrc element
appsrc = pipeline.get_by_name("source")

# Set caps for appsrc
width, height, framerate = 640, 480, 30
caps = Gst.Caps.from_string(
    f"video/x-raw,format=BGR,width={width},height={height},framerate={framerate}/1"
)
appsrc.set_property("caps", caps)

# Function to push frames into appsrc
def push_data():
    # Generate a simple pattern (or use your video frame source)
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, f"Appsrc Video {push_data.counter}", (50, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    # Convert the frame to a GStreamer buffer
    data = frame.tobytes()
    buf = Gst.Buffer.new_allocate(None, len(data), None)
    buf.fill(0, data)
    push_data.counter += 1
    buf.pts = buf.dts = Gst.util_uint64_scale(int(push_data.counter * 1e9 / framerate), 1, 1)
    buf.duration = Gst.util_uint64_scale(int(1e9 / framerate), 1, 1)
    # buf.duration = 0
    # duration_ns = int(1e9 / framerate)
    # buf.pts = buf.dts = push_data.counter * duration_ns
    # buf.duration = duration_ns
    # GLib.log_default_handler("MyApp", GLib.LogLevelFlags.LEVEL_MESSAGE, f"This {push_data.counter}")
    # Push the buffer to appsrc
    retval = appsrc.emit("push-buffer", buf)
    if retval != Gst.FlowReturn.OK:
        print("Error pushing buffer:", retval)
        loop.quit()
    push_data.counter
    return True

# Initialize the counter for frame timestamps
push_data.counter = 0

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Start pushing frames periodically
loop = GLib.MainLoop()
GLib.timeout_add(1000 // framerate, push_data)

try:
    print("Playing video with appsrc. Press Ctrl+C to stop.")
    loop.run()
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # Stop the pipeline
    appsrc.emit("end-of-stream")
    pipeline.set_state(Gst.State.NULL)
