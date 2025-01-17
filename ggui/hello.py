import gi
gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gst, Gtk, GdkX11, GstVideo

class VideoPlayer:
    def __init__(self):
        # Initialize GStreamer
        Gst.init(None)

        # Create GTK Window
        self.window = Gtk.Window()
        self.window.set_title("GStreamer Video Player")
        self.window.set_default_size(800, 600)
        self.window.connect("destroy", self.on_destroy)

        self.vbox = Gtk.VBox()
        self.window.add(self.vbox)

        # Create Drawing Area for Video
        self.drawing_area = Gtk.DrawingArea()
        self.vbox.pack_start(self.drawing_area, expand=True, fill=True, padding=0)

        # Create a Button Box
        self.button_box = Gtk.HButtonBox()
        self.vbox.pack_start(self.button_box, expand=False, fill=True, padding=10)

        # Add Play/Pause Button
        self.play_button = Gtk.Button(label="Play")
        self.play_button.connect("clicked", self.on_play_button_clicked)
        self.button_box.pack_start(self.play_button, expand=False, fill=False, padding=5)


        # # Create GStreamer Pipeline
        # self.pipeline = Gst.parse_launch(
        #     "playbin uri=file:///path/to/your/video.mp4"
        # )

        # # Get the video sink from playbin and set it to the DrawingArea
        # self.video_sink = self.pipeline.get_by_name("video-sink")
        # self.drawing_area.connect("realize", self.on_realize)

        # Show GUI
        self.window.show_all()

    def on_play_button_clicked(self, button):
        self.play_button.set_label("Play")
        print("ffff")

    def on_realize(self, widget):
        # Get window handle
        window = self.drawing_area.get_window()
        window_handle = window.get_xid()

        # Set the video sink's window handle
        if self.video_sink:
            self.video_sink.set_window_handle(window_handle)

        # Start the pipeline
        self.pipeline.set_state(Gst.State.PLAYING)

    def on_destroy(self, widget):
        # Stop the pipeline and clean up
        self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit()

# Main Function
if __name__ == "__main__":
    player = VideoPlayer()
    Gtk.main()
