# $Id$
# -*- coding: gbk -*-
import sys
import os
import tempfile
import argparse

import tov_consts
import lzss
from util import get_getter

verbose = 1
debug = False

def decompress(data):
	if not data:
		return data
	get = get_getter(data, "<")
	comtype = get(0x0, "B")
	comsize = get(0x1, "I")
	decomsize = get(0x5, "I")
	if comtype in (0x1, 0x3) and comsize + 9 == len(data):	# lzss
		if comtype == 0x1: handler = lzss.decompress_lz01
		else: handler = lzss.decompress_lz03
		data = handler(data[9:], lzss.init_text_buf)
	elif get(0x0, "I") == 0xEE12F50F:	# xbcompress
		temp_fd, temp_path = tempfile.mkstemp(".DAT")
		temp_fp = open(temp_path, "wb")
		temp_fp.write(data)
		temp_fp.close()
		os.system(".\\script\\quickbms.exe decompressor.bms %s %s" % (temp_path, os.path.split(temp_path)[0]))
		data = open(temp_path.replace(".DAT", ".unpacked"), "rb").read()
	return data

# returns: is_splitted
def split(data, root=".", depth=0):
	indent = ("==" * depth) + "> "
	# decompress (if compressed)
	data = decompress(data)
	
	# after decompression
	get = get_getter(data, ">")
	fourcc = data[:4]
	if fourcc != "FPS4":
		return False
	
	# if FPS4, need split further
	file_count = get(0x4, "I")
	header_size = get(0x8, "I")
	file_data_offset = get(0xc, "I")
	assert header_size == 0x1C, "header size should be a constant"
	
	file_descriptor_size = get(0x10, "H")
	file_descriptor_flag = get(0x12, "H")
	assert (file_descriptor_flag & tov_consts.FILE_DESCRIPTOR_MINIMUM) == tov_consts.FILE_DESCRIPTOR_MINIMUM, "least bitflag set not matched!"
	
	assert get(0x14, "I") == 0x0, "should be reserved!"
	
	string_table_offset = get(0x18, "I")
	
	noname_idx = 0
	empty_idx = 0
	last_filename = ""
	mdl_part_count = 0
				
	# dump each file
	for i in xrange(file_count):
		base_offset = offset = header_size + file_descriptor_size * i
				
		# file offset
		file_offset = get(offset, "I")
		offset += 4
		if file_offset == 0xFFFFFFFF:
			assert not any(get(offset, "%dI" % (file_descriptor_size / 4 - 1))), "empty file descriptor, other fields should all be zero!"
		else:
			# file size
			file_size = get(offset, "I")
			offset += 4
			real_file_size = get(offset, "I")
			offset += 4
			# file data
			file_data = data[file_offset: file_offset + real_file_size]
			file_data = decompress(file_data)
			# file name
			if file_descriptor_flag & tov_consts.FILE_DESCRIPTOR_FILE_NAME:
				file_name = get(offset, "32s").rstrip("\x00").upper()
				offset += 0x20
			else:
				file_name = ""
			if not file_name and (last_filename.endswith(".SPM") or last_filename.endswith(".TXM")):
				file_name = last_filename[:-1] + "V"
			# file ext
			if "." in file_name and (not file_name.endswith(".DAT")):
				ext = "." + file_name.split(".")[-1]
			elif real_file_size > 0:
				get2 = get_getter(file_data, ">")
				file_type = get2(0x0, "I")
				# short ext
				ext = tov_consts.TYPE_2_EXT.get(file_type)
				# long ext
				if ext is None and get2(0x0, "8s").rstrip("\x00\x20") in tov_consts.LONG_TYPES:
					ext = "." + get2(0x0, "8s").rstrip("\x00\x20")
				if ext is None:
					ext = ""
					#raise Exception("unknown extension type! 0x%x or %s or %s @ 0x%x" % (file_type, file_data[:4], file_data[:8], file_offset))
			else:
				ext = ""
			if mdl_part_count > 0 and not file_name:
				file_name = os.path.splitext(last_filename)[0] + ext
			mdl_part_count -= 1
			# resolve file name by various hint
			if not file_name:
				if real_file_size == 0:
					file_name = "EMPTY%d" % empty_idx
					empty_idx += 1
				else:
					file_name = "NONAME%d%s" % (noname_idx, ext)
					noname_idx += 1
			
			# unknown: bit4
			if file_descriptor_flag & tov_consts.FILE_DESCRIPTOR_BIT4:
				unk = get(offset, "I")
				if unk != 0:
					raise Exception("unk field = 0x%x @ offset = 0x%x" % (unk, offset))
				offset += 0x4
				
			# datatype, e.g.MDL
			if file_descriptor_flag & tov_consts.FILE_DESCRIPTOR_DATA_TYPE:
				data_type = get(offset, "4s").rstrip("\x00")
				offset += 0x4
			else:
				data_type = ""
			
			if data_type == "MDL":
				mdl_part_count = 9
				
			# argument
			arg = ""
			if file_descriptor_flag & tov_consts.FILE_DESCRIPTOR_ARG:
				arg_off = get(offset, "I")
				offset += 0x4
				if arg_off > 0:
					assert arg_off >= string_table_offset, "invalid arg offset 0x%x" % arg_off
					arg = data[arg_off: data.find("\x00", arg_off)]
			# is_dir
			is_dir = (ext == ".FPS4")
			# path hint
			if arg:
				if ext in (".FPS4", ".T8BTMO"):
					file_name = arg.replace("/", "_") + ext
				elif ext in (".ANM", ".BLD", ".CLS", ".HRC", ".MTR", ".SHD", ".SPM", ".SPV", ".TXM", ".TXV"):
					if "/" in arg:
						file_name = arg.replace("/", "_") + ext
				elif ext in (".TO8FOGD", ".TO8LITD", ".TO8PSTD", ".TO8SKYD", ".TO8WTRD", ".TO8SK2D"):
					env = arg
					
				# write arg out for later check
				if not os.path.exists(root): os.mkdir(root)
				arg_list_fname = os.path.join(root, "arg_list.txt")
				f_arg_list = open(arg_list_fname, "a+")
				f_arg_list.write("%s %s\n" % (file_name, arg))
				f_arg_list.close()
				
			# unknown: bit7
			if file_descriptor_flag & tov_consts.FILE_DESCRIPTOR_BIT7:
				unk = get(offset, "I")
				if unk != 0:
					raise Exception("unk field = 0x%x @ offset = 0x%x" % (unk, offset))
				offset += 0x4
			
			if verbose > 0:
				line = "off=0x%x, name:%s, 0x%x~0x%x" % (base_offset, file_name, file_offset, file_offset + real_file_size)
				if arg:
					line += ", arg:%s" % arg
				if data_type:
					line += ", data_type:%s" % data_type
				print indent + line

			# make output folder
			if not os.path.exists(root):
				os.mkdir(root)
				
			force_save = debug
			if force_save:
				f = open(os.path.join(root, file_name), "wb")
				f.write(file_data)
				f.close()
			
			if verbose > 1:
				print os.path.join(root, file_name)
				
			if os.path.exists(os.path.join(root, file_name)):
				continue
			
			need_split = split(file_data, root=os.path.join(root, os.path.splitext(file_name)[0]), depth=depth+1)
			
			if (not need_split) and (not force_save):
				f = open(os.path.join(root, file_name), "wb")
				f.write(file_data)
				f.close()
			
			last_filename = file_name
				
	return True

if __name__ == '__main__':
	description = "Split a FPS4 files into minimum chunks."
	
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument("-f", action="store", dest="fps4_file", type=argparse.FileType("rb"), help="Input file, the fps4 file.")
	parser.add_argument("-o", action="store", dest="out_dir", type=str, help="Output file, the unpack root directory.")
	
	args = parser.parse_args()
	
	data = args.fps4_file.read()
	
	if verbose > 1:
		print "==================="
		print args.fps4_file.name
		print "==================="
		
	if args.out_dir is not None:
		root = args.out_dir
	else:
		root = ".\\split\\%s" % os.path.splitext(os.path.split(args.fps4_file.name)[1])[0]
		
	# may missing files that do not need split
	split(data, root=root)
	