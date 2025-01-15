import gi
import numpy as np
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

NUM_FRAMES = 50

PIPE = "videotestsrc ! fpsdisplaysink"
PIPE = f"videotestsrc num-buffers={NUM_FRAMES} ! video/x-raw,framerate=10/1 ! fpsdisplaysink"

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