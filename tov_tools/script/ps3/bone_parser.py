import sys
import struct
import argparse

FILE_TYPE = 0x100

# makes parsing data a lot easier
def get_getter(data, endian):
	def get(offset, fmt):
		size = struct.calcsize(fmt)
		res = struct.unpack(endian + fmt, data[offset: offset + size])
		if len(res) == 1:
			return res[0]
		return res
	return get
	
def parse(data):
	get = get_getter(data, ">")
	
	file_type = get(0x0, "I")
	assert file_type == FILE_TYPE, "Unknown file type, not a bone file!"
	file_size = get(0x4, "I")
	assert file_size == len(data), "Invalid file, file size dismatch, may be corrupted!"
	platform = get(0x8, "I")
	assert platform == 0x10, "Invalid file, this file may not from PS3 version!"
	bone_count = get(0xc, "I")
	mat_offset = get(0x18, "I")
	
	bone_ids = get(0x1c, "%dI" % bone_count)
	
	offset = 0x1c + bone_count * 0x4
	for i in xrange(bone_count):
		bname_off = get(offset+0x18, "I")
		bname_off += offset+0x18
		
		bname = data[bname_off: data.find("\x00", bname_off)]
		
		print "Bone ID = 0x%04x, Name = %s" % (bone_ids[i], bname)
		offset += 0x20
	
	
	
if __name__ == '__main__':
	
	description = "Parse bone hierachy of Tales of Vesperia(PS3 ver) model file."
	
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument("-f", action="store", dest="bone_file", type=argparse.FileType("rb"), help="Input file, the bone file.")
	
	args = parser.parse_args()
	
	data = args.bone_file.read()
	
	parse(data)