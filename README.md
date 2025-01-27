

```bash
sudo apt install libcairo2-dev pkg-config
sudo apt install libgirepository1.0-dev gobject-introspection
```

```bash
pip install pycairo PyGObject
```


| file  | desc  |
|---|---|
| video_to_mpeg  | save video as mpegts  |

---

## usage
- run demo.py to create `MISB.ts` file
- Extract data using ffmpeg 
- parse and show data using
  - klvdata_test.py
  - parser_demo.py


## extract KLV

```bash
ffprobe data/output/MISB.ts 
#
Duration: 00:01:02.07, start: 3600.000000, bitrate: 60549 kb/s
  Program 1 
  Stream #0:0[0x41]: Video: h264 (High 4:4:4 Predictive) (HDMV / 0x564D4448), yuv444p(tv, bt709, progressive), 3840x2160 [SAR 1:1 DAR 16:9], 30 fps, 30 tbr, 90k tbn, 60 tbc
  Stream #0:1[0x42]: Data: klv (KLVA / 0x41564C4B)
```

```
ffmpeg -i MISB.ts -map 0:1 -c copy -f data misb.klv
```

```
python gst_klv/klvdata_test.py < data/output/misb.klv 
```

```
python /home/user/projects/gst_klv/gst_klv/parse_demo.py
```

---

# Reference
- [QGISFMV](https://github.com/All4Gis/QGISFMV?tab=readme-ov-file)
- [Python code for muxing klv and video (MISB)](https://gist.github.com/All4Gis/509fbe06ce53a0885744d16595811e6f)
- [KlvOverMpegTSExtractor](https://github.com/shacharmo/KlvOverMpegTSExtractor)
- [pypi klvdata](https://pypi.org/project/klvdata/)


```
Jon Krohn
```

pip3 install cuda-python
https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/blob/master/bindings/README.md


cd deepstream_python_apps/bindings
python3 setup.py install