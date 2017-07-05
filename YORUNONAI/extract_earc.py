import sys
import os
from util import get_getter
from util import swap_fourCC

EARC = swap_fourCC("EARC")

def extract(path):
	f = open(path, "rb")
	data = f.read()
	f.close()
	
	get = get_getter(data, "<")
	
	fourcc = get(0x0, "4s")
	assert fourcc == EARC, "invalid EARC file!"
	unk = get(0x4, "I")
	if unk != 0x01:
		assert False, "warning: not 0x01"
	
	data_size = get(0x8, "I")
	header_size = get(0xc, "I")
	filelist_size = get(0x10, "I")
	
	file_count = get(0x14, "I")
	unk = get(0x18, "I")

	# assertion fails on PC version
	# if unk != 1:
	# 	assert False, "warning: not 1"
	
	fixed_offset = get(0x1c, "I")
	
	root = os.path.splitext(path)[0]
	if not os.path.exists(root):
		os.mkdir(root)
	base_offset = 0x1c
	last_off = None
	for i in xrange(file_count):
		off, size, filename = get(base_offset + i * 0x38, "2I48s")
		filename = filename.rstrip("\x00")
		# print "index: 0x%x raw_off: 0x%x" % (i, off)
		
		# we should always use calculated offset for extracting file
		# offset in the file will cause empty gap in memory, which is reserved for thoese 'dummy'(I guess)
		off = (off - fixed_offset + header_size + filelist_size)
		if last_off is not None and off != last_off:
			off = last_off
		end_off = off + size
		last_off = end_off
		
		# print "%03d: %s @0x%x -> 0x%x" % (i, filename, off, end_off)
		assert filename == "dummy" or size != 0, "empty file always use name 'dummy'"
		
		if size == 0:
			continue
		
		out_path = os.path.join(root, filename)
		fout = open(out_path, "wb")
		fout.write(data[off: off + size])
		fout.close()
		
	assert end_off == len(data), "file size not invalid!! 0x%x vs 0x%x" % (end_off, len(data))
	
if __name__ == '__main__':
	extract(sys.argv[1])