# 
#  Write KLV data from file using gst
# 
import gi
import numpy as np
import cv2
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import time

# Initialize GStreamer
Gst.init(None)

# Create the GStreamer pipeline
pipeline_description = ("appsrc name=klv-source is-live=True \
    ! meta/x-klv \
    ! filesink location=data/output.mxf"
)
pipeline = Gst.parse_launch(pipeline_description)

# Get the appsrc element
appsrc = pipeline.get_by_name("klv-source")

width, height, framerate = 640, 480, 5

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
# Function to push frames into appsrc
def push_data():
    key = b'\x01'  # Example key
    data = f"hello {push_data.counter}"
    value = data.encode('utf-8')
    klv_bytes = encode_klv(key, value)
    klv_packet_size = len(klv_bytes)
    push_data.counter +=1
    # KLV Data
    #print(klv_bytes)
    if(klv_bytes==b'' or push_data.counter==10):
        print("End klv stream")
        appsrc.emit("end-of-stream")
        exit(0)
    
    klvbuf = Gst.Buffer.new_allocate(None, klv_packet_size, None)
    klvbuf.fill(0, klv_bytes)

    # buf.pts = buf.dts = Gst.util_uint64_scale(int(push_data.counter * 1e9 / framerate), 1, 1)
    # buf.duration = Gst.util_uint64_scale(int(1e9 / framerate), 1, 1)
    duration_ns = int(1e9 / framerate)
    klvbuf.pts = klvbuf.dts = push_data.counter * duration_ns
    klvbuf.duration = duration_ns
    GLib.log_default_handler("MyApp", GLib.LogLevelFlags.LEVEL_MESSAGE, f"This {push_data.counter}")
    # Push the buffer to appsrc
    retval = appsrc.emit("push-buffer", klvbuf)
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
