# 
# generate a simple video stream using appsrc and control video rate
import cairo
import gi
import numpy as np
import cv2
gi.require_version('Gst', '1.0')
gi.require_foreign('cairo')
from gi.repository import Gst, GLib
from fastapi import FastAPI
import threading
app = FastAPI()

# Initialize GStreamer
Gst.init(None)

def on_draw(_overlay, context, _timestamp, _duration):
    """Each time the 'draw' signal is emitted"""
    context.select_font_face('Open Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    context.set_font_size(40)
    context.move_to(100, 100)
    context.text_path('HELLO')
    context.set_source_rgb(0.5, 0.5, 1)
    context.fill_preserve()
    context.set_source_rgb(0, 0, 0)
    context.set_line_width(1)
    context.stroke()

"""
gst-launch-1.0 udpsrc port=5000 \
! 'application/x-rtp, encoding-name=H264, payload=96' \
! rtph264depay \
! h264parse \
! avdec_h264 \
! videoconvert \
! fpsdisplaysink sync=false
"""

# Create the GStreamer pipeline
pipeline_description = ("""appsrc name=source is-live=true  format=time \
    ! videoconvert \
    ! queue leaky=downstream max-size-buffers=1 \
    ! videorate name=rate \
    ! capsfilter name=capsfilter caps=video/x-raw,framerate=5/1 \
    ! videoconvert \
    ! cairooverlay name=overlay \
    ! videoconvert \
    ! x264enc tune=zerolatency threads=4 speed-preset=ultrafast \
    ! rtph264pay \
    ! udpsink host=127.0.0.1 port=5000 sync=true"""
)
pipeline = Gst.parse_launch(pipeline_description)

# Get the appsrc element
appsrc = pipeline.get_by_name("source")
cairo_overlay = pipeline.get_by_name('overlay')
cairo_overlay.connect('draw', on_draw)
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
    # buf.pts = buf.dts = Gst.util_uint64_scale(int(push_data.counter * 1e9 / framerate), 1, 1)
    # buf.duration = Gst.util_uint64_scale(int(1e9 / framerate), 1, 1)
    buf.pts = buf.dts = 0
    buf.duration = 0
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

def change_fps(rate):
    videorate = pipeline.get_by_name("rate")
    capsfilter = pipeline.get_by_name("capsfilter")
    # videorate.get_static_pad("src").set_caps(Gst.Caps.from_string(f"video/x-raw,framerate={rate}/1"))
    capsfilter.set_property("caps", Gst.Caps.from_string(f"video/x-raw,framerate={rate}/1"))
def fps_change(fps):
    try:
        print(f"Changing fps to {fps}")
        GLib.idle_add(change_fps, fps)
    finally:
        return True

# Initialize the counter for frame timestamps
push_data.counter = 0
# Start the pipeline
def start_pipeline():
    pipeline.set_state(Gst.State.PLAYING)

    # Start pushing frames periodically
    loop = GLib.MainLoop()
    GLib.timeout_add(1000 // framerate, push_data)
    # GLib.timeout_add(5000, fps_change)
    try:
        print("Playing video with appsrc. Press Ctrl+C to stop.")
        loop.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Stop the pipeline
        appsrc.emit("end-of-stream")
        pipeline.set_state(Gst.State.NULL)
# Start the GStreamer pipeline in a separate thread

@app.post("/update-rate/{rate}")
async def update_rate(rate: int):
    fps_change(rate)
    return {"message": f"rate updated to {rate} fps"}

def start_gstreamer_thread():
    threading.Thread(target=start_pipeline, daemon=True).start()

if __name__ == "__main__":
    # Start GStreamer in a background thread
    start_gstreamer_thread()

    # Run the FastAPI app using Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)