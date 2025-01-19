import cairo
import gi
import queue

gi.require_version('Gst', '1.0')
# gi.require_foreign('cairo')
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)
klv_queue = queue.Queue(maxsize=10)

def on_draw(_overlay, context, _timestamp, _duration):
        """Each time the 'draw' signal is emitted"""
        data = klv_queue.get(timeout=1)
        context.select_font_face('Open Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(40)
        context.move_to(100, 100)
        context.text_path(data)
        context.set_source_rgb(0.5, 0.5, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.set_line_width(1)
        context.stroke()

def bus_callback(bus, message, loop):
    """
    Handle GStreamer bus messages.
    """
    if message.type == Gst.MessageType.EOS:
        print("End-of-stream received, exiting.")
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"Error: {err}, Debug Info: {debug}")
        loop.quit()
    return True

pipeline_description = """
udpsrc port=5000 ! tsdemux name=demux \
demux. ! multiqueue name=mq ! video/x-h264 ! decodebin  ! videoconvert ! cairooverlay name=overlay  ! videoconvert !  autovideosink sync=false
demux. ! mq. mq. ! meta/x-klv ! appsink name=klv_sink

"""
pipeline = Gst.parse_launch(pipeline_description)
appsink = pipeline.get_by_name("klv_sink")
counter = 0
# cairo_overlay = pipeline.get_by_name('overlay')


def parse_klv(klv_data):
    i = 0
    while i < len(klv_data):
        key = klv_data[i]
        length = klv_data[i + 1]
        value = klv_data[i + 2 : i + 2 + length]
        str_value = value.decode('utf-8')
        i += 2 + length
    return str_value

def on_new_sample(sink):
    sample = appsink.emit('pull-sample')
    buffer = sample.get_buffer()
    success, mapinfo = buffer.map(Gst.MapFlags.READ)
    if success:
        # Here you can process the KLV data
        klv_data = mapinfo.data
        i = 0
        data = parse_klv(klv_data)
        try:
            klv_queue.put(data, timeout=1)
        except queue.Full:
            print("KLV queue is full, dropping data")
        buffer.unmap(mapinfo)
        
    return Gst.FlowReturn.OK



# Set the appsink properties
appsink.set_property("emit-signals", True)
appsink.connect("new-sample", on_new_sample)

cairo_overlay = pipeline.get_by_name('overlay')
cairo_overlay.connect('draw', on_draw)

pipeline.set_state(Gst.State.PLAYING)

bus = pipeline.get_bus()
bus.add_signal_watch()
loop = GLib.MainLoop()
bus.connect("message", bus_callback, loop)

try:
    print("Playing video with appsrc. Press Ctrl+C to stop.")
    loop.run()
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # Stop the pipeline
    
    pipeline.set_state(Gst.State.NULL)