import sys
import struct

FILE_TYPE = 0x400
HEADER_SIZE = 0x14

# makes parsing data a lot easier
def get_getter(data, endian):
	def get(offset, fmt):
		size = struct.calcsize(fmt)
		res = struct.unpack(endian + fmt, data[offset: offset + size])
		if len(res) == 1:
			return res[0]
		return res
	return get
	
def hex_format(data):
	size = len(data)
	bytes_data = struct.unpack("%dB"%size, data)
	str_list = []
	for i in xrange(size / 4):
		str_list.append("%02x %02x %02x %02x" % tuple(bytes_data[i*4:i*4+4]))
	return " | ".join(str_list)
	
def parse(data):
	get = get_getter(data, ">")
	
	file_type = get(0x0, "I")
	assert file_type == FILE_TYPE, "Invalid file! Not a morph file! type=0x%x" % file_type
	file_size = get(0x4, "I")
	assert file_size == len(data), "Invalid file! File size doesn't match! 0x%x vs 0x%x" % (file_size, len(data))
	unk1 = get(0x8, "I")				# kind of file format version thing!
	track_count = get(0xc, "I")
	unk3 = get(0x10, "f")				# some float, 2000.0 etc
	
	if unk1 == 0x2:
		offset = HEADER_SIZE
		for i in xrange(track_count):
			track_type, track_size = get(offset, "II")
			print hex_format(data[offset: offset + track_size])
			offset += track_size
			
		assert offset == file_size, "Unknown data remains!!"
	elif unk1 == 0x4:
		offset = HEADER_SIZE
		for i in xrange(track_count):
			track_size, track_type = get(offset, "HH")
			track_size *= 4		# convert unit to byte
			print hex_format(data[offset: offset + track_size])
			offset += track_size
		assert offset == file_size, "Unknown data remains!!"
	elif unk1 == 0x10:
		offset = HEADER_SIZE
	else:
		assert False, "Unknown track format type! 0x%x" % unk1
	
if __name__ == '__main__':
	data = open(sys.argv[1], "rb").read()
	parse(data)
