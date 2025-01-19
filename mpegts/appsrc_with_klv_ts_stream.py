# 
# generate video and klv data and send it with mpegts over UDP
# Gen video and push it to appsrc
# Gen KLV message and push it to appsrc
#


import gi
import numpy as np
import cv2
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

# Create the GStreamer pipeline
pipeline_description = (
    "mpegtsmux name=mux alignment=7  ! udpsink host=127.0.0.1 port=5000 sync=true \
    appsrc name=source is-live=true  format=time ! videoconvert ! queue ! x264enc tune=zerolatency threads=4  ! mux. \
    appsrc name=klv_source is-live=true format=time ! meta/x-klv,parsed=true !  mux. "
)
pipeline = Gst.parse_launch(pipeline_description)

# Get the appsrc element
appsrc = pipeline.get_by_name("source")
klv_appsrc = pipeline.get_by_name("klv_source")
# Set caps for appsrc
width, height, framerate = 640, 480, 5
caps = Gst.Caps.from_string(
    f"video/x-raw,format=BGR,width={width},height={height},framerate={framerate}/1"
)
appsrc.set_property("caps", caps)

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

def encode_klv(key: bytes, value: bytes) -> bytes:
    """
    Encodes a Key-Length-Value (KLV) triplet.

    :param key: The key as a byte string.
    :param value: The value as a byte string.
    :return: Encoded KLV as a byte string.
    """
    # Encode the length using BER TLV (Basic Encoding Rules for Length)
    length = len(value)
    if length < 128:
        length_bytes = length.to_bytes(1, 'big')  # Short form: single byte
    else:
        # Long form: first byte indicates the number of length bytes
        length_bytes = b'\x80' + length.to_bytes((length.bit_length() + 7) // 8, 'big')
    
    # Combine key, length, and value
    klv = key + length_bytes + value
    return klv

def gen_frame(id:int) -> bytes:
    # Generate a simple pattern (or use your video frame source)
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, f"Appsrc Video {id}", (50, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    # Convert the frame to a GStreamer buffer
    data = frame.tobytes()
    return data

def gen_klv(id) -> bytes:
    key = b'\x01'  # Example key
    data = f"hello {id}"
    value = data.encode('utf-8')
    klv_bytes = encode_klv(key, value)
    return klv_bytes

def push_data():
    data = gen_frame(push_data.counter)
    buf = Gst.Buffer.new_allocate(None, len(data), None)
    buf.fill(0, data)

    duration_ns = int(1e9 / framerate)
    buf.pts = buf.dts = push_data.counter * duration_ns
    buf.duration = duration_ns
    GLib.log_default_handler("MyApp", GLib.LogLevelFlags.LEVEL_MESSAGE, f"This {push_data.counter}")
    # Push the buffer to appsrc
    retval = appsrc.emit("push-buffer", buf)
    if retval != Gst.FlowReturn.OK:
        print("Error pushing buffer:", retval)
        loop.quit()

    ## klv buffer
    klv_bytes = gen_klv(push_data.counter)
    klv_packet_size = len(klv_bytes)
    klvbuf = Gst.Buffer.new_allocate(None, klv_packet_size, None)
    klvbuf.fill(0, klv_bytes)
    klvbuf.pts = buf.dts = push_data.counter * duration_ns
    klvbuf.duration = duration_ns
    retval = klv_appsrc.emit("push-buffer", klvbuf)
    if retval != Gst.FlowReturn.OK:
        print("Error pushing buffer:", retval)
        loop.quit()
    ## klv buffer
    
    push_data.counter += 1
    if push_data.counter >= 300:  # Stop after 10 iterations
        print("Exiting timeout loop. send eos")
        appsrc.emit("end-of-stream")
        klv_appsrc.emit("end-of-stream")
        return False  # Returning False stops the timeout
    return True

# Initialize the counter for frame timestamps
push_data.counter = 0

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

bus = pipeline.get_bus()
bus.add_signal_watch()
loop = GLib.MainLoop()
bus.connect("message", bus_callback, loop)
GLib.timeout_add(1000 // framerate, push_data)

try:
    print("Playing video with appsrc. Press Ctrl+C to stop.")
    loop.run()
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # Stop the pipeline
    
    pipeline.set_state(Gst.State.NULL)
