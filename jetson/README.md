```
gst-launch-1.0 videotestsrc name=source is-live=true \
    ! videoconvert \
    ! cairooverlay name=overlay \
    ! queue leaky=upstream max-size-buffers=1 \
    ! videorate name=rate \
    ! capsfilter name=capsfilter caps=video/x-raw,framerate=5/1 \
    ! video/x-raw ! nvvidconv ! 'video/x-raw(memory:NVMM)' \
    ! nvv4l2h264enc  bitrate=500000 control-rate=constant_bitrate preset-level=UltraFastPreset maxperf-enable=true qp-range="20,40:23,43:25,45" \
    ! rtph264pay \
    ! udpsink host=10.0.0.1 port=5000 sync=true
```

```
gst-launch-1.0 videotestsrc ! videoconvert ! timeoverlay time-mode=6  font-desc="Courier Bold, 90"  ! autovideosink
```

gst-launch-1.0 videotestsrc name=source is-live=true \
    ! video/x-raw,framerate=30/1 \
    ! videoconvert \
    ! timeoverlay font-desc="Courier Bold, 90" \
    ! tee name=t \
    ! queue \
    ! videorate ! video/x-raw,framerate=30/1 ! videoconvert ! autovideosink sync=false \
    t. \
    ! queue leaky=upstream max-size-buffers=1 \
    ! videorate name=rate \
    ! capsfilter name=capsfilter caps=video/x-raw,framerate=2/1 \
    ! video/x-raw ! nvvidconv ! 'video/x-raw(memory:NVMM)' \
    ! nvv4l2h264enc  bitrate=500000 control-rate=constant_bitrate \
        preset-level=UltraFastPreset \
        maxperf-enable=true \
        qp-range="20,40:23,43:25,45" \
        insert-sps-pps=1 \
        iframeinterval=100 \
    ! rtph264pay  \
    ! udpsink host=10.0.0.1 port=5000 sync=false
```

```
gst-launch-1.0 udpsrc port=5000  \
! 'application/x-rtp, encoding-name=H264, payload=96' \
! rtph264depay \
! h264parse \
! avdec_h264 \
! videoconvert \
! fpsdisplaysink sync=false

```

! videorate ! video/x-raw,framerate=20/1

```bash title="pc stream"
gst-launch-1.0 -v videotestsrc is-live=true \
    ! video/x-raw,framerate=15/1 ! videoconvert \
    ! timeoverlay font-desc="Courier Bold, 90" \
    ! tee name=t \
    ! queue  ! videoconvert ! autovideosink sync=false t. \
    ! queue  leaky=downstream max-size-buffers=2   ! videorate ! video/x-raw,framerate=1/1 ! videoconvert \
    ! x264enc tune=zerolatency bitrate=1000 speed-preset=ultrafast \
    ! rtph264pay  \
    ! udpsink host=127.0.0.1 port=5000 sync=true
```

```
gst-launch-1.0 \
    videotestsrc is-live=true ! video/x-raw,framerate=30/1 ! videoconvert ! tee name=t \
    t. ! queue ! videorate ! video/x-raw,framerate=5/1 ! fpsdisplaysink \
    t. ! queue ! fpsdisplaysink
```

```
gst-launch-1.0 \
    videotestsrc is-live=true ! video/x-raw,framerate=30/1 ! videoconvert ! tee name=t \
    t. ! queue ! videorate ! video/x-raw,framerate=5/1 ! fpsdisplaysink \
    t. ! queue ! fpsdisplaysink
```