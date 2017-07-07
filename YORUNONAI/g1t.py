import struct
import os
import sys
import util
from PIL import Image
from consts import G1TG0060

# dont know why the same header works for Dragon Crown don't work for YoruNoNaiKuni
def gen_dxt1_header(width, height):
	header = "\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x08\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x04\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	return header[:0xc] + struct.pack("<II", height, width) + header[0x14:]

def tex_extract(path):
	f = open(path, "rb")
	data = f.read()
	f.close()
	
	get = util.get_getter(data, "<")
	fourcc = get(0x0, "8s")
	assert fourcc == G1TG0060, "invalid or unsupported g1t file!"

	file_size, header_size = get(0x8, "II")
	tex_count = get(0x10, "I")
	
	tex_off_list = get(header_size, "%dI" % tex_count, force_tuple=True)
	base_off = header_size

	# split
	for i in xrange(tex_count):
		out_path = path + ".tex%d" % i
		if not os.path.exists(out_path):
			off = base_off + tex_off_list[i]
			end_off = file_size if (i + 1 >= tex_count) else (base_off + tex_off_list[i + 1])
			tex_blk = data[off: end_off]
			fout = open(out_path, "wb")
			fout.write(tex_blk)
			fout.close()

	# convert
	for i in xrange(tex_count):
		out_path = path + ".tex%d" % i
		f = open(out_path, "rb")
		tex_blk = f.read()
		f.close()
		print "conv texture %d" % i
		conv_tex(tex_blk, out_path)


TEXTYPE_DXT1 = {
	"name": "DXT1",
	"com_rate": 8,
}

TEXTYPE_DXT3 = {
	"name": "DXT3/DXT5",
	"com_rate": 4,
}

TEXTYPE_RAW = {
	"name": "RAW",
	"com_rate": 1,
}

TEXTYPES = {
	0x6: TEXTYPE_DXT1,
	0x8: TEXTYPE_DXT3,
	0x1: TEXTYPE_RAW,
	0x9: TEXTYPE_DXT1,
	0xB: TEXTYPE_DXT3,
}

def conv_tex(data, out_path):
	get = util.get_getter(data, "<")

	_mip_count = get(0x0, "B");
	mip_count = (_mip_count >> 4);
	print "mip_count = ", mip_count

	_dds_type = get(0x1, "B")
	dds_type = (_dds_type & 0xF);

	assert dds_type in TEXTYPES, "unknown texture type: 0x%x" % dds_type

	dim = get(0x2, "B")
	tex_h = 1 << (dim >> 4)
	tex_w = 1 << (dim & 0xF)
	print "size = (%d, %d)" % (tex_w, tex_h)

	com_rate = TEXTYPES[dds_type]["com_rate"]

	# skip unknown fields
	unk = get(0x7, "B")
	assert unk in (0x10, 0x0), "unknown fields 0x%x" % unk
	if unk == 0x10:
		tex_data_off = 0x14
	else:
		tex_data_off = 0x8

	# print hex(tex_data_off)

	mip0_size = tex_w * tex_h * 4
	unzip_size = 0
	# print "mip0_size", mip0_size
	for i in xrange(mip_count):
		unzip_size += mip0_size / (4 ** i)
	# print "total_size:", unzip_size

	print "filesize: 0x%x, calcsize: 0x%x" % ((len(data) - tex_data_off) * com_rate, unzip_size)
	assert (len(data) - tex_data_off) * com_rate == unzip_size


	body = data[tex_data_off:]

	type_info = TEXTYPES[dds_type]
	# mipmap can be dropped
	if type_info["name"] == "DXT1":
		print "DXT1"
		fcontent = gen_dxt1_header(tex_w, tex_h)
		fcontent += body
		f = open(out_path + ".dds", "wb")
		f.write(fcontent)
		f.close()		
	elif type_info["name"] == "DXT3/DXT5":	# DXT3 or DXT5
		print "DXT3/DXT5"
		fcontent = util.gen_dxt5_header(tex_w, tex_h)
		fcontent += body
		f = open(out_path + ".dds", "wb")
		f.write(fcontent)
		f.close()
	# This Game use the following types in lightmaps(or effect texture) only, which I don't bother to fix
	else:
		print type_info["name"]
		image = Image.frombytes("RGBA", (tex_w, tex_h), body)
		image.save(out_path + ".png")
		
if __name__ == '__main__':
	tex_extract(sys.argv[1])