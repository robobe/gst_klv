import gi
import keyboard

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib


class VideoPlayer:
    def __init__(self):
        # Initialize GStreamer
        Gst.init(None)

        # Create the pipeline
        self.pipeline = Gst.parse_launch(
            "videotestsrc is-live=true ! videoconvert ! autovideosink"
        )

        # Start the pipeline
        self.pipeline.set_state(Gst.State.PLAYING)

        # Initialize playback rate
        self.playback_rate = 1.0

        # Start key listener in a separate thread
        self.start_key_listener()

    def set_playback_rate(self, rate):
        """Set the playback rate by adjusting the pipeline's segment seek."""
        self.playback_rate = rate
        # Perform a flush seek to adjust playback speed
        event = Gst.Event.new_seek(
            self.playback_rate,
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
            Gst.SeekType.SET,
            0,
            Gst.SeekType.NONE,
            -1,
        )
        self.pipeline.send_event(event)
        print(f"Playback rate set to: {self.playback_rate}x")

    def start_key_listener(self):
        """Start listening for key presses to change properties."""
        def key_listener():
            print("Press '+' to increase speed, '-' to decrease speed, or 'q' to quit.")
            while True:
                if keyboard.is_pressed("+"):
                    self.set_playback_rate(self.playback_rate + 0.1)
                    keyboard.wait("+")  # Avoid repeated triggers

                elif keyboard.is_pressed("-"):
                    self.set_playback_rate(max(0.1, self.playback_rate - 0.1))
                    keyboard.wait("-")

                elif keyboard.is_pressed("q"):
                    print("Exiting...")
                    GLib.MainLoop().quit()
                    break

        # Run the listener in a separate thread
        import threading

        threading.Thread(target=key_listener, daemon=True).start()


def main():
    player = VideoPlayer()

    # Run the GStreamer main loop
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        player.pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    main()
