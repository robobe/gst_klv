#!/bin/bash

gst-launch-1.0 udpsrc port=5000  buffer-size=65536 \
! 'application/x-rtp, encoding-name=H264, payload=96' \
! rtpjitterbuffer latency=10 \
! rtph264depay \
! h264parse \
! avdec_h264 \
! videoconvert \
! fpsdisplaysink sync=false