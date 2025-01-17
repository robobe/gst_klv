import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

pipeline = Gst.Pipeline.new("dynamic-compositor-pipeline")

# Create the compositor
compositor = Gst.ElementFactory.make("compositor", "compositor")
pipeline.add(compositor)

# Add a sink for displaying the composed video
sink = Gst.ElementFactory.make("autovideosink", "video-sink")
pipeline.add(sink)
compositor.link(sink)

def add_source(pipeline, compositor, pattern=0):
    # Create a new video source
    source = Gst.ElementFactory.make("videotestsrc", None)
    source.set_property("pattern", pattern)
    pipeline.add(source)
    
    # Create a video convert element
    video_convert = Gst.ElementFactory.make("videoconvert", None)
    pipeline.add(video_convert)
    
    # Link the source to the video converter
    source.link(video_convert)

    # Create a new pad for the compositor
    sink_pad = compositor.get_request_pad("sink_%u")
    print(f"Adding source: {sink_pad.get_name()}")
    
    # Link the video converter to the compositor
    video_convert.link(compositor)

    # Set the source to PLAYING
    source.set_state(Gst.State.PLAYING)
    video_convert.set_state(Gst.State.PLAYING)

    return source, video_convert


def remove_source(pipeline, compositor, source, video_convert):
    # Unlink and release the pad
    sink_pad = video_convert.get_static_pad("src").get_peer()
    compositor.release_request_pad(sink_pad)

    # Set elements to NULL state
    source.set_state(Gst.State.NULL)
    video_convert.set_state(Gst.State.NULL)

    # Remove elements from the pipeline
    pipeline.remove(source)
    pipeline.remove(video_convert)
    print(f"Removed source: {sink_pad.get_name()}")


pipeline.set_state(Gst.State.PLAYING)

# Add a source dynamically
source1, video_convert1 = add_source(pipeline, compositor, pattern=0)

# Add another source after 5 seconds
GLib.timeout_add_seconds(5, lambda: add_source(pipeline, compositor, pattern=1))

# Remove the first source after 10 seconds
GLib.timeout_add_seconds(10, lambda: remove_source(pipeline, compositor, source1, video_convert1))

# Run the main loop
loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    pass

# Cleanup
pipeline.set_state(Gst.State.NULL)