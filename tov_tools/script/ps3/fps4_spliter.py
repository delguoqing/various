import sys
import struct
import argparse
import os

MAGIC_CODE = "FPS4"

FLAG_TOP_LEVEL  = 0x000C0007
FLAG_TOP_LEVEL2 = 0x00140067
FLAG_SUB_LEVEL  = 0x00100047

FLAG_SET = (FLAG_TOP_LEVEL, FLAG_SUB_LEVEL, FLAG_TOP_LEVEL2)

# makes parsing data a lot easier
def get_getter(data, endian):
	def get(offset, fmt):
		size = struct.calcsize(fmt)
		res = struct.unpack(endian + fmt, data[offset: offset + size])
		if len(res) == 1:
			return res[0]
		return res
	return get

# data: fps4 file content
# list_blocks: boolean. If true, then sub blocks are only listed not extracted.
# block_idx_to_extract: integer.
def split(data, list_blocks, block_idx_to_extract, out_folder):
	is_fps4 = data.startswith(MAGIC_CODE)
	if not is_fps4:
		raise Exception("unknown data block type!")
	
	get = get_getter(data, ">")
	
	sub_block_count = get(0x4, "I")		# how many sub-block is contained in this FPS4 block
	header_size = get(0x8, "I")			# always 0x1C ?
	sub_block_offset = get(0xC, "I")	# where does the 1st sub-block start?
	flag = get(0x10, "I")				# 00 0C 00 07 -- a top level fps4 block?
										# 00 10 00 47 -- a sub level fps4 block?
										
	assert flag in FLAG_SET, "unknown flags!! %s" % hex(flag)
	zero1 = get(0x14, "I")
	if zero1 != 0:
		print "wrong guess, it is not zero"

	filename_off = get(0x18, "I")
	
	# skip header
	base_offset = header_size
	
	if flag == FLAG_TOP_LEVEL:
		
		sub_block_data = []	# sub fps4-block data
	
		# check if each sub block is a valid fps4 block(starts with 'FPS4')
		for block_idx in xrange(sub_block_count - 1):
			fmt = "III"
			offset, size1, size2 = get(base_offset, fmt)
			base_offset += struct.calcsize(fmt)
			
			magic_code = get(offset, "4s")
			if magic_code == MAGIC_CODE:
				if block_idx == block_idx_to_extract:
					print "block @ %s, size = (%s, %s)" % tuple(map(hex, (offset, size1, size2)))
					sub_block_data.append(data[offset: offset + size1])
			else:
				print "direct sub, @ %s, size = (%s, %s)" % tuple(map(hex, (offset, size1, size2)))
				out_file = os.path.join(out_folder, "sub%d.bin" % block_idx)
				open(out_file, "wb").write(data[offset: offset + size2])
			
		for sub_data in sub_block_data:
			print "============="
			split(sub_data, list_blocks, block_idx_to_extract, out_folder)
		
	elif flag == FLAG_TOP_LEVEL2:
		
		for block_idx in xrange(sub_block_count - 1):
			fmt = "III4sI"
			offset, size1, size2, str_type, fname_off = get(base_offset, fmt)
			base_offset += struct.calcsize(fmt)
			
			if fname_off == 0x0:
				fname = ""
			else:
				fname = data[filename_off: data.find("\x00", filename_off)]
			str_type = str_type.rstrip("\x00")
			
			print "direct sub, name=%s,type=%s @ %s, size = (%s, %s)" % ((fname, str_type) + tuple(map(hex, (offset, size1, size2))))
			out_file = os.path.join(out_folder, "sub%d.bin" % block_idx)
			open(out_file, "wb").write(data[offset: offset + size2])			
		
	elif flag == FLAG_SUB_LEVEL:

		for block_idx in xrange(sub_block_count - 1):
			fmt = "IIII"
			offset, size1, size2, dirname_off = get(base_offset, fmt)
			base_offset += struct.calcsize(fmt)
			
			########
			## debug
			########
			offset += 0x80
			
			dirname = data[dirname_off: data.find("\x00", dirname_off)]
			print "block %d @[%s,%s,%s], dir=%s" % ((block_idx,) + tuple(map(hex, (offset, offset+size2, offset+size1))) + (dirname, ))
			
			########
			## debug
			########
			if not list_blocks:
				offset -= 0x80
				folder = os.path.join(out_folder, dirname)
				if not os.path.exists(folder):
					os.system("mkdir %s" % os.path.normpath(folder))
				out_file = os.path.join(folder, "sub%d.bin" % (block_idx%10))
				if not os.path.exists(out_file):
					open(out_file, "wb").write(data[offset: offset+size2])
			
	# after all these (offset, size1, size2) pair
	# follows a total file size?
	file_size = get(base_offset, "I")
	#assert file_size == len(data), "wrong guess, this is not file size"
	
if __name__ == '__main__':
	description = "Split an FPS4 file from Tales of Vesperia into sub files."
	
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument("-l", action="store_true", default=False, dest="list_blocks", help="List blocks, but don't extract.")
	parser.add_argument("-f", action="store", dest="fps4_file", type=argparse.FileType("rb"), help="Input file, the unpacked fps4 file.")
	parser.add_argument("-i", action="store", dest="block_idx", type=int, default=0)
	parser.add_argument("-o", action="store", default=".", dest="out_folder", type=str, help="Output folder, where the splitted files will go to.")
	
	args = parser.parse_args()
	
	data        = args.fps4_file.read()
	list_blocks = args.list_blocks
	block_idx   = args.block_idx
	out_folder  = args.out_folder

	filename = os.path.split(args.fps4_file.name)[1]
	
	print "===>"
	print "===> Parsing: %s" % filename
	print "===>"
	
	try:
		split(data, list_blocks, block_idx, out_folder)
	except Exception, e:
		print e
		sys.stderr.write("\n")
		sys.stderr.write("===>Error In Parsing: %s\n" % filename)