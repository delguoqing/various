import struct
import os
import sys
import util
import Image

# dont know why the same header works for Dragon Crown don't work for YoruNoNaiKuni
def gen_dxt1_header(width, height):
	header = "\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x08\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x04\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	return header[:0xc] + struct.pack("<II", height, width) + header[0x14:]

def tex_extract(path):
	f = open(path, "rb")
	data = f.read()
	f.close()
	
	get = util.get_getter(data, ">")
	fourcc = get(0x0, "8s")
	assert fourcc == "G1TG0060", "invalid or unsupported g1t file!"

	file_size, header_size = get(0x8, "II")
	tex_count = get(0x10, "I")
	
	tex_off_list = get(header_size, "%dI" % tex_count, force_tuple=True)
	base_off = header_size
	
	for i in xrange(tex_count):
		out_path = path + ".tex%d" % i
		if not os.path.exists(out_path):
			off = base_off + tex_off_list[i]
			end_off = file_size if (i + 1 >= tex_count) else (base_off + tex_off_list[i + 1])
			tex_blk = data[off: end_off]
			fout = open(out_path, "wb")
			fout.write(tex_blk)
			fout.close()
		else:
			f = open(out_path, "rb")
			tex_blk = f.read()
			f.close()
		
		print "conv texture %d" % i
		conv_tex(tex_blk, out_path)
		
def conv_tex(data, out_path):
	get = util.get_getter(data, ">")
	mip_count = get(0x0, "B")
	# print "mip_count", mip_count
	dds_type = get(0x1, "B")
	
	assert dds_type in (0x6, 0x8, 0x9, 0x1), "maybe dds type, 0x6 = DXT1, 0x8 = DXT3/DXT5, 0x9:no compression"
	
	dim = get(0x2, "B")
	tex_w = 1 << (dim >> 4)
	tex_h = 1 << (dim & 0xF)
	
	if dds_type == 0x6:
		com_rate = 8
	elif dds_type == 0x8:
		com_rate = 4
	elif dds_type == 0x1 or dds_type == 0x9:
		com_rate = 1
		
	# print "dim:", tex_w, tex_h
	mip0_size = tex_w * tex_h * 4
	unzip_size = 0
	# print "mip0_size", mip0_size
	for i in xrange(mip_count):
		unzip_size += mip0_size / (4 ** i)
	# print "total_size:", unzip_size
	
	# skip some unknown block	
	off = 0x8
	unk_count = get(0x7, "B")
	for i in xrange(unk_count):
		off += get(off, "I")
		
	tex_data_off = off
	# print hex(tex_data_off)
	tex_data_size = len(data) - tex_data_off
	
	assert tex_data_size * com_rate == unzip_size, "0x%x, 0x%x, %d" % (tex_data_size, unzip_size,
																	   unzip_size / tex_data_size)
	body = data[tex_data_off:]
	# mipmap can be dropped
	if dds_type == 0x6: # DXT1
		print "DXT1"
		fcontent = gen_dxt1_header(tex_w, tex_h)
		fcontent += body
		f = open(out_path + ".dds", "wb")
		f.write(fcontent)
		f.close()		
	elif dds_type == 0x8:	# DXT3 or DXT5
		print "DXT3/DXT5"
		fcontent = util.gen_dxt5_header(tex_w, tex_h)
		fcontent += body
		f = open(out_path + ".dds", "wb")
		f.write(fcontent)
		f.close()
	# This Game use the following types in lightmaps(or effect texture) only, which I don't bother to fix
	elif dds_type == 0x1:
		print "RAW0x1"
		image = Image.fromstring("RGBA", (tex_w, tex_h), body)
		image.save(out_path + ".png")
	elif dds_type == 0x9:
		print "RAW0x9"
		image = Image.fromstring("RGBA", (tex_w, tex_h), body)
		image.save(out_path + ".png")
		
if __name__ == '__main__':
	tex_extract(sys.argv[1])