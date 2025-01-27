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
pipeline_description = ("""input-selector name=selector 
            v4l2src device=/dev/video0 ! video/x-raw,framerate=30/1 ! queue ! selector.sink_0 
            videotestsrc pattern=1 is-live=true ! video/x-raw,framerate=30/1 ! queue ! selector.sink_1  \
    selector. \
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
selector = pipeline.get_by_name("selector")
# Get the appsrc element

cairo_overlay = pipeline.get_by_name('overlay')
cairo_overlay.connect('draw', on_draw)




def change_fps(rate):
    videorate = pipeline.get_by_name("rate")
    capsfilter = pipeline.get_by_name("capsfilter")
    # videorate.get_static_pad("src").set_caps(Gst.Caps.from_string(f"video/x-raw,framerate={rate}/1"))
    capsfilter.set_property("caps", Gst.Caps.from_string(f"video/x-raw,framerate={rate}/1"))

def change_source(id):
    stream_mapping = {
            1: "sink_0",
            2: "sink_1"
        }
        # TODO: check current and not switch if request current
    if id in stream_mapping:
        pad_name = stream_mapping[id]
        request_pad = selector.get_static_pad(pad_name)
        selector.set_property("active-pad", request_pad)


def fps_change(fps):
    try:
        print(f"Changing fps to {fps}")
        GLib.idle_add(change_fps, fps)
    finally:
        return True

def source_change(id):
    try:
        print(f"Changing source {id}")
        GLib.idle_add(change_source, id)
    finally:
        return True

# Initialize the counter for frame timestamps
# Start the pipeline
def start_pipeline():
    pipeline.set_state(Gst.State.PLAYING)

    # Start pushing frames periodically
    loop = GLib.MainLoop()
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

@app.post("/switch-source/{id}")
async def switch_source(id: int):
    source_change(id)
    return {"message": f"source updated to {id}"}

def start_gstreamer_thread():
    threading.Thread(target=start_pipeline, daemon=True).start()

if __name__ == "__main__":
    # Start GStreamer in a background thread
    start_gstreamer_thread()

    # Run the FastAPI app using Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)