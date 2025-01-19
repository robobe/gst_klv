import cv2
import gi
import numpy as np
import queue
import threading

gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

# Frame queue
frame_queue = queue.Queue(maxsize=10)

# Worker function for the GStreamer pipeline
def gstreamer_worker():
    # GStreamer pipeline
    pipeline = Gst.parse_launch(
        "videotestsrc ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink"
    )

    # Get the appsink element
    appsink = pipeline.get_by_name("sink")
    appsink.set_property("emit-signals", False)  # Disable signals
    appsink.set_property("drop", True)          # Drop old frames if the queue is full

    # Start the pipeline
    pipeline.set_state(Gst.State.PLAYING)

    try:
        while True:
            # Pull a sample from appsink
            sample = appsink.emit("pull-sample")
            if not sample:
                print("End of stream or error")
                break

            # Get the buffer and map it
            buffer = sample.get_buffer()
            success, map_info = buffer.map(Gst.MapFlags.READ)
            if not success:
                continue

            # Extract frame data and dimensions
            frame_data = np.frombuffer(map_info.data, dtype=np.uint8)
            caps = sample.get_caps()
            structure = caps.get_structure(0)
            width = structure.get_int("width")[1]
            height = structure.get_int("height")[1]

            # Reshape frame into OpenCV-compatible format
            frame = frame_data.reshape((height, width, 3))

            # Unmap the buffer
            buffer.unmap(map_info)

            # Put the frame into the queue
            try:
                frame_queue.put(frame, timeout=1)
            except queue.Full:
                print("Frame queue is full, dropping frame")

    except Exception as e:
        print(f"GStreamer error: {e}")

    # Clean up
    pipeline.set_state(Gst.State.NULL)

# Start GStreamer thread
gstreamer_thread = threading.Thread(target=gstreamer_worker, daemon=True)
gstreamer_thread.start()

# Main thread: Wait for frames and display them
try:
    while True:
        try:
            # Wait for a frame from the queue
            frame = frame_queue.get(timeout=1)
            # Display the frame using OpenCV
            cv2.imshow("GStreamer OpenCV", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except queue.Empty:
            print("No frame received in time")

except KeyboardInterrupt:
    print("Stopping...")

# Clean up OpenCV
cv2.destroyAllWindows()
