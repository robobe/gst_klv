import gi
import numpy as np
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

# Frame generation settings
WIDTH = 640
HEIGHT = 480
FPS = 30
NUM_FRAMES = 100

# Global counter to track the number of frames sent
frame_count = 0

# Callback for the need-data signal
def on_need_video_data(appsrc, length):
    global frame_count
    print(frame_count)
    if frame_count >= NUM_FRAMES:
        # If we have sent enough frames, send an EOS (End of Stream) signal
        appsrc.emit("end-of-stream")
        return

    # Create a simple test frame (e.g., a solid color with a moving square)
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    x_pos = (frame_count * 5) % WIDTH
    frame[:, x_pos:x_pos+50] = [0, 255, 0]  # Green square

    # Convert the frame to a GStreamer buffer
    buffer = Gst.Buffer.new_wrapped(frame.tobytes())

    # Push the buffer to the appsrc
    appsrc.emit("push-buffer", buffer)

    # Increment the frame count
    frame_count += 1

# Create the GStreamer pipeline
pipeline = Gst.parse_launch(
    "appsrc name=src is-live=true format=3 caps=video/x-raw,format=RGB,width=640,height=480,framerate=1/1 \
    ! videoconvert \
    ! queue max-size-buffers=1 leaky=downstream \
        ! videorate \
        ! video/x-raw, framerate=1/1 \
    ! x264enc ! mp4mux ! filesink location=output.mp4"
)

# Get the appsrc element
appsrc = pipeline.get_by_name("src")

# Connect the need-data signal to the callback
appsrc.connect("need-data", on_need_video_data)

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Run the main loop
loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    pass

# Clean up
pipeline.set_state(Gst.State.NULL)
