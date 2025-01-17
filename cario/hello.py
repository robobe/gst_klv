import cairo
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_foreign('cairo')
from gi.repository import Gst, GObject, Gtk

class GstCairoExample(object):
    """Example class to generate user interface and create new GStreamer pipeline"""
    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title('Gstreamer cairo overlay')
        window.set_default_size(300, -1)
        window.connect('delete-event', Gtk.main_quit)
        vbox = Gtk.VBox()
        window.add(vbox)
        self.button = Gtk.Button('Start')
        self.button.connect('clicked', self.start_stop)
        vbox.add(self.button)
        window.show_all()

        self.pipeline = Gst.parse_launch(
            'videotestsrc ! cairooverlay name=overlay ! videoconvert ! xvimagesink')
        cairo_overlay = self.pipeline.get_by_name('overlay')
        cairo_overlay.connect('draw', self.on_draw)

    def on_draw(self, _overlay, context, _timestamp, _duration):
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

    def start_stop(self, _button):
        """When button is pressed to start or stop the GStreamer pipeline"""
        if self.button.get_label() == 'Start':
            self.button.set_label('Stop')
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            self.pipeline.set_state(Gst.State.NULL)
            self.button.set_label('Start')

GObject.threads_init()
Gst.init(None)
GstCairoExample()
Gtk.main()