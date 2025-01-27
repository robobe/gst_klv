import klvdata

if __name__ == "__main__":
	with open('/home/user/projects/gst_klv/data/klvdata.bin', 'rb') as f:
		for packet in klvdata.StreamParser(f):
			packet.structure()