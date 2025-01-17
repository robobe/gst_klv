# Gstreamer

## Basic Concepts
### Elements
- Source
- Filters, converter, mux, demux, codec
- Sink

[gst-dev](https://gstreamer.freedesktop.org/documentation/application-development/basics/elements.html?gi-language=c)
### Pads
- Connection points between elements
- Source pads produce data
- Sink pads consume data
- Data always flows from src to sink pad
- Can operate in **pull** or **push** mode

### Pad caps
- Each pad have a predefined set of properties called **Capabilities** or **Caps**
- Caps are used to validate the communication between elements (caps **restrict the type of data flows** through it)
- A source pad can only be linked to a sink pad if their allowed data type are compatible
- Elements can negotiate with other on format to use (caps negotiation)

### Bins
- Elements can be grouped into a container called **bin**

### Pipeline
- It provides a bus for communication purposes
- It runs in a separate thread

### Synchronization
- GstClock objects provide clock time
- GstClock always returns the **absolute-time**
- Sink elements are responsible for present the buffer in their respective presentation time
  - If a buffer is delayed the sink drops it