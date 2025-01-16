## Control pipe frame rate

appsrc_rate: control video rate and show the result using fpsdisplaysink
appsrc_rate_stream: stream the control fps video using h264 and UDP
appsrc_rate_stream_dynamic: change to fps dynamically using glib thread
appsrc_rate_stream_dynamic_web: do the same from web api using fastapi
appsrc_rate_stream_dynamic_gtk: use gtk to change fps 

**GLib.idle_add**
GLib.idle_add is a utility function in the GLib library used to schedule a callback to be executed when the main loop is idle

!!! Tip
    Ask chat "why its good practice to change pipe properties when the loop is idle"