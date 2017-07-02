import os
import sys
import struct
import zlib

def decomp(path):
	print "decompressing", path
	f = open(path, "rb")
	data = f.read()
	f.close()
	
	file_no = 0
	off = 0x0
	end_off = len(data)
	data_out = ""
	while off < end_off:
		blk_size = struct.unpack("<I", data[:4])[0]
		if blk_size == 0:
			break
		print "off 0x%x, size 0x%x" % (off, blk_size)
		blk_data = data[4: 4 + blk_size]
		
		fout_old = path.replace(".gz", ".gz.%d" % file_no)
		if os.path.exists(fout_old):
			os.remove(fout_old)
		data_out += zlib.decompress(blk_data)
		
		off += blk_size + 4
		data = data[blk_size + 4:]
		file_no += 1
		
	f = open(path.replace(".gz", ""), "wb")
	f.write(data_out)
	f.close()
	
if __name__ == '__main__':
	decomp(sys.argv[1])