# 
#  Read KLV data from file using gst
# 
import gi
import numpy as np
import cv2
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import time

# Initialize GStreamer
Gst.init(None)

def on_new_sample(sink):
    """
    Callback function triggered when appsink receives a new sample.
    Extracts and processes the raw KLV data.
    """
    sample = sink.emit("pull-sample")
    if not sample:
        return Gst.FlowReturn.EOS

    buffer = sample.get_buffer()
    success, mapinfo = buffer.map(Gst.MapFlags.READ)
    if success:
        klv_data = mapinfo.data
        print(f"Received raw KLV data: {klv_data.hex()}")

        # Example of parsing KLV packets manually
        # Assuming KLV format: Key (1 byte), Length (1 byte), Value (Length bytes)
        i = 0
        while i < len(klv_data):
            key = klv_data[i]
            length = klv_data[i + 1]
            value = klv_data[i + 2 : i + 2 + length]
            GLib.log_default_handler("MyApp", GLib.LogLevelFlags.LEVEL_MESSAGE, f"KLV Packet - Key: {key}, Length: {length}, Value: {value.hex()}")
            str_value = value.decode('utf-8')
            GLib.log_default_handler("MyApp", GLib.LogLevelFlags.LEVEL_MESSAGE, str_value)
            i += 2 + length

        buffer.unmap(mapinfo)

    return Gst.FlowReturn.OK

# Create the GStreamer pipeline
pipeline_description = ("filesrc location=data/output.mxf \
    ! meta/x-klv ! appsink name=klv emit-signals=True sync=False"
)
pipeline = Gst.parse_launch(pipeline_description)

# Get the appsrc element
appsink = pipeline.get_by_name("klv")

appsink.connect("new-sample", on_new_sample)
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

# Initialize the counter for frame timestamps

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Start pushing frames periodically
loop = GLib.MainLoop()
# GLib.timeout_add(1000 // framerate, push_data)

try:
    print("Playing video with appsrc. Press Ctrl+C to stop.")
    loop.run()
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # Stop the pipeline
    pipeline.set_state(Gst.State.NULL)
