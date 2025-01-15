import gi
import numpy as np
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

OUTPUT_FILE = "data/output.mp4"

PIPE = f"filesrc location={OUTPUT_FILE} ! decodebin ! videoconvert !fpsdisplaysink"

pipeline = Gst.parse_launch(PIPE)
pipeline.set_state(Gst.State.PLAYING)

# Run the main loop
loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    pass

# Clean up
pipeline.set_state(Gst.State.NULL)