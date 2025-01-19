import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import threading
import queue
import numpy as np
import cv2

Gst.init(None)

# Queues for video frames and KLV data
video_queue = queue.Queue(maxsize=10)
klv_queue = queue.Queue(maxsize=10)

def parse_klv(klv_data):
    i = 0
    while i < len(klv_data):
        key = klv_data[i]
        length = klv_data[i + 1]
        value = klv_data[i + 2 : i + 2 + length]
        str_value = value.decode('utf-8')
        i += 2 + length
    return str_value

def gstreamer_worker():
    # Define the pipeline
    pipeline_description = """
udpsrc port=5000 ! tsdemux name=demux \
demux. ! multiqueue name=mq ! video/x-h264 ! decodebin ! videoconvert ! video/x-raw,format=BGR ! appsink name=video_sink
demux. ! mq. mq. ! meta/x-klv ! appsink name=klv_sink
"""
    pipeline = Gst.parse_launch(pipeline_description)

    # Get the appsinks
    video_sink = pipeline.get_by_name("video_sink")
    klv_sink = pipeline.get_by_name("klv_sink")

    # Configure appsinks
    for sink in [video_sink, klv_sink]:
        sink.set_property("emit-signals", False)
        sink.set_property("drop", True)
        # sink.set_property("sync", False)

    # Start the pipeline
    pipeline.set_state(Gst.State.PLAYING)

    try:
        while True:
            # Pull video frames
            video_sample = video_sink.emit("pull-sample")
            if video_sample:
                buffer = video_sample.get_buffer()
                success, map_info = buffer.map(Gst.MapFlags.READ)
                if success:
                    caps = video_sample.get_caps()
                    structure = caps.get_structure(0)
                    width = structure.get_int("width")[1]
                    height = structure.get_int("height")[1]
                    frame_data = np.frombuffer(map_info.data, dtype=np.uint8)
                    frame = frame_data.reshape((height, width, 3))
                    buffer.unmap(map_info)
                    try:
                        video_queue.put(frame, timeout=1)
                    except queue.Full:
                        print("Video frame queue is full, dropping frame")

            # Pull KLV data
            klv_sample = klv_sink.emit("pull-sample")
            if klv_sample:
                buffer = klv_sample.get_buffer()
                success, map_info = buffer.map(Gst.MapFlags.READ)
                if success:
                    klv_data = bytes(map_info.data)
                    buffer.unmap(map_info)
                    data = parse_klv(klv_data)
                    try:
                        klv_queue.put(data, timeout=1)
                    except queue.Full:
                        print("KLV queue is full, dropping data")
    except Exception as e:
        print(f"GStreamer error: {e}")
    finally:
        pipeline.set_state(Gst.State.NULL)

# Main thread to process and display frames
def main():
    thread = threading.Thread(target=gstreamer_worker, daemon=True)
    thread.start()
    data = ""
    try:
        while True:
             # Process KLV metadata
            try:
                klv_data = klv_queue.get(timeout=1)
                data = str(klv_data)
                print(f"KLV Data: {klv_data}")

            except queue.Empty:
                pass

            # Process video frames

            try:
                fframe = video_queue.get_nowait()
                frame = fframe.copy()
                cv2.putText(frame, data, (0,300), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

                cv2.imshow("Video", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            except queue.Empty:
                print("No video frame received in time")

           
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
