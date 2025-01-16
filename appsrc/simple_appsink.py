import cv2
import gi
import numpy as np
import queue
import threading

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

frame_queue = queue.Queue(maxsize=10)  # Thread-safe queue for frames


def gst_to_opencv(buffer, caps):
    """Convert GStreamer buffer to OpenCV image."""
    structure = caps.get_structure(0)
    width = structure.get_int("width")[1]
    height = structure.get_int("height")[1]
    format_str = structure.get_string("format")

    if format_str not in ["BGR", "RGB"]:
        raise ValueError(f"Unsupported format: {format_str}")

    success, map_info = buffer.map(Gst.MapFlags.READ)
    if not success:
        raise RuntimeError("Failed to map GStreamer buffer")

    frame_data = np.frombuffer(map_info.data, dtype=np.uint8)
    frame = frame_data.reshape((height, width, 3))  # 3 channels for BGR/RGB
    buffer.unmap(map_info)
    return frame


def on_new_sample(sink):
    """Callback for new samples from appsink."""
    sample = sink.emit("pull-sample")
    if not sample:
        return Gst.FlowReturn.ERROR

    buffer = sample.get_buffer()
    caps = sample.get_caps()

    try:
        frame = gst_to_opencv(buffer, caps)
        if not frame_queue.full():
            frame_queue.put(frame)  # Add frame to the queue
    except Exception as e:
        print(f"Error converting buffer: {e}")
        return Gst.FlowReturn.ERROR

    return Gst.FlowReturn.OK


def opencv_display():
    """Main loop for OpenCV display."""
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()  # Get the frame from the queue
            cv2.imshow("Frame", frame)

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                GLib.MainLoop().quit()
                break


def main():
    Gst.init(None)

    pipeline_description = (
        "videotestsrc ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink"
    )
    pipeline = Gst.parse_launch(pipeline_description)

    appsink = pipeline.get_by_name("sink")
    appsink.set_property("emit-signals", True)
    appsink.set_property("sync", False)
    appsink.connect("new-sample", on_new_sample)

    pipeline.set_state(Gst.State.PLAYING)

    # Run OpenCV display in the main thread
    opencv_thread = threading.Thread(target=opencv_display, daemon=True)
    opencv_thread.start()

    # Run GStreamer main loop
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        pipeline.set_state(Gst.State.NULL)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
