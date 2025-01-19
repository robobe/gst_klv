

- appsrc_ts: write frame from appsrc to mpegts file with h264 stream
- appsrc_with_klv_ts: crate mpegts file that contain h264 video and klv data
- read_klv_from_ts: read klv data from mpegts file parse and print data
- read_klv_from_ts_and_play: read data and play video 
- appsrc_with_klv_ts_stream.py: stream mpegts over udp with h264 video and klv data
- play_ts_stream.py: play mpegts video and parse klv from udp stream

## Demo

terminal1: stream video and klv over udp
terminal2: play the stream and split it to video and klv data

split terminals

```bash title="terminal1"
 python /home/user/projects/gst_klv/mpegts/appsrc_with_klv_ts_stream.py
```

```bash title="terminal2"
python /home/user/projects/gst_klv/mpegts/play_ts_stream.py
```