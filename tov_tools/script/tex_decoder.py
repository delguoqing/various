import sys
import os
import struct
import StringIO
import Image

DOA_FMT_TABLE = {
	2:("L8",1),
	0x86:("A8R8G8B8",4),
	0x4A:("G8R8",2),
	0x52:("DXT1",8),
	0x53:("DXT3",16),
	0x54:("DXT5",16),
	0x71:("DXN",16),
	0x7B:("DXT5A",8),
}
	
# makes parsing data a lot easier
def get_getter(data, endian):
	def get(offset, fmt):
		size = struct.calcsize(fmt)
		res = struct.unpack(endian + fmt, data[offset: offset + size])
		if len(res) == 1:
			return res[0]
		return res
	return get
	
def untiletextures(infile, outpath, doafmt, Width, Height, inBuffOffset):
	if doafmt not in DOA_FMT_TABLE: return
		
	l = open(infile, "rb")
	
	textype, mipmaps, istiled, istiledoffset = ("TX2D", 0, True, 0)
	
	#print("\n", rfilename, "\n", lfilename, sep = "")
	
	dxfmt, TexelPitch = DOA_FMT_TABLE[doafmt]#DXN = ATI2 ;G8R8 - 0x4a
	Sides, ddsVar27, ddsVar28 = (1, 0x1000, 0)
	if textype == 'TXCM':
		 Sides, ddsVar27, ddsVar28 = (6, 0x1008, 0xFE00) #sides = 6 textures from cube texture
	textypenote = {'TX3D':"\t(volumemap)", 'TXCM':"\t(cubemap)", 'TX2D':""}[textype]

	noMipSize = int(Width * Height * {0x52:0.5, 0x86:4, 0x4A:2}.get(doafmt, 1)) * Sides
	ddsCap = [0x20534444, 0x7C, 0x81007, Height, Width, noMipSize] + [0]*(32-6)
	ddsCap[19] = 0x20
	ddsCap[27] = ddsVar27
	ddsCap[28] = ddsVar28
	ddsCap[20] = {0x86:0x41, 0x4A:0x20001, 2:0x20000}.get(doafmt,4)
	ddsCap[21] = {0x52:0x31545844, 0x53:0x33545844, 0x54:0x35545844, 0x71:0x32495441}.get(doafmt,0)#fourcc
	if doafmt in (0x86,0x71):
		ddsCap[22:27] = [0x20, 0xFF0000, 0xFF00, 0xFF, 0xFF000000]
		if doafmt == 0x71:
			ddsCap[7] = 1
	elif doafmt == 2:
		ddsCap[22:24] = [8, 0xFF]
	elif doafmt == 0x4A:
		ddsCap[22:25] = [0x10, 0xFF00, 0xFF]
	#print("%3d"%(count-i), "%8s"%dxfmt, "%4d"%Width, "x", "%4d"%Height, "m%d"%mipmaps, texname, textypenote)
	#outpath = outdir + '/' + texnameZ
##			with io.BytesIO() as sf:
	sf = open(outpath, "wb")

	fnc = 1 if doafmt in (2, 0x86, 0x4A) else 4
	if textype != 'TX3D':
		tiledWidth = int((Width+fnc-1)/fnc)
		tiledHeight = int((Height+fnc-1)/fnc) * Sides
		if textype == 'TXCM' and export_cubic_and_volumetric_as_2D:
			ddsCap[27] = 0x1000		
			ddsCap[28] = 0
			ddsCap[3] = int(Height*6)
		sf.write(struct.pack("32L", *ddsCap))
		if istiled:
			Untile360(sf, l, inBuffOffset, TexelPitch, tiledWidth, tiledHeight)
		else:
			l.seek(inBuffOffset)
			texdata = l.read(noMipSize)
			if TexelPitch == 1:
				sf.write(texdata)
			else:
				if TexelPitch == 4:
					for j in range(0,noMipSize,4):
						sf.write(struct.pack("<L", struct.unpack(">L", texdata[j:j+4])[0]))
				else:
					for j in range(0,noMipSize,2):
						sf.write(struct.pack("<H", struct.unpack(">H", texdata[j:j+2])[0]))
	else:
		tiledWidth = int((Width*2+fnc-1)/fnc)#include both textures from doa5 volume texture
		tiledHeight = int((Height*2+fnc-1)/fnc)#include both textures from doa5 volume texture
		
		tempstream = StringIO.StringIO()
		ddsCap[5] = noMipSize*2
		if not export_cubic_and_volumetric_as_2D:
			ddsCap[2] &= 0x800000
			ddsCap[6] = 2
			ddsCap[28] = 0x200000
		else:
			ddsCap[3] = int(Height*2)
		sf.write(struct.pack("32L", *ddsCap))
		if istiled:
			Untile360(tempstream, l, inBuffOffset, TexelPitch, tiledWidth, tiledHeight)
			fixDoa5VolumeTexture(sf, tempstream, TexelPitch, Width*2, Height*2)
		else:
			l.seek(inBuffOffset)
			texdata = l.read(noMipSize*2)
			if TexelPitch == 1:
				sf.write(texdata)
			else:
				tempbuf = StringIO.StringIO()
				tempbuf.write(texdata)
				tempbuf.seek(0)
				if TexelPitch == 4:
					for j in range(noMipSize*2//4):
						sf.write(struct.pack("<L", struct.unpack(">L", tempbuf.read(4))[0]))
				else:
					for j in range(noMipSize*2//2):
						sf.write(struct.pack("<H", struct.unpack(">H", tempbuf.read(2))[0]))

	l.close()
	sf.close()


def Untile360(outBuff, inBuff, inBuffOffset, TexelPitch, Width, Height):
	v12 = 1 << ((TexelPitch >> 4) - (TexelPitch >> 2) + 3)
	v51 = (TexelPitch >> 2) + (TexelPitch >> 1 >> (TexelPitch >> 2))
	v36 = ~(v12 - 1) & v12
	v42 = ~(v12 - 1) & Width
	rectWidth = (Width if Width < v36 else v36)
	for i in range(Height):
		v47 = (((Width + 0x1F) & 0xFFFFFFE0) >> 5) * (i >> 5)
		v44 = (i >> 4) & 1
		v46 = 16 * (i & 1) + (((i >> 3) & 1) << (v51 + 6))
		v41 = 4 * (i & 6)
		v45 = 0xFF & (2 * ((i >> 3) & 1))
		v22 = v46  + (((v41 << (v51 + 6)) >> 6) & 0xF) + 2 * ((((v41 << (v51 + 6)) >> 6) & 0xFFFFFFF0) + ((v47 << (v51 + 6)) & 0x1FFFFFFF))
		sourceOff = inBuffOffset + 8 * ((v22 & 0xFFFFFE00) + 4 * (((v44 + 2 * (v45 & 3)) & 0xFFFFFFFE) + 8 * (((v22 >> 6) & 7) + 8 * (((0xFF & v44) + 2 * (v45 & 3)) & 1)))) + (v22 & 0x3F)
		untilechunk(outBuff, inBuff, sourceOff, rectWidth << v51, TexelPitch)
		v48 = v36
		while ( v48 < v42 ):
			v25 = ((v41 + (v48 & 7)) << (v51 + 6)) >> 6
			v26 = v46 + (v25 & 0xF) + 2 * ((v25 & 0xFFFFFFF0) + (((v47 + (v48 >> 5)) << (v51 + 6)) & 0x1FFFFFFF))
			v27 = v44 + 2 * ((v45 + (0xFF & (v48 >> 3))) & 3)
			v28 = ((v26 >> 6) & 7) + 8 * (((0xFF & v44) + 2 * ((v45 + (0xFF & (v48 >> 3))) & 3)) & 1)
			sourceOff =  inBuffOffset + 8 * ((v26 & 0xFFFFFE00) + 4 * ((v27 & 0xFFFFFFFE) + 8 * v28)) + (v26 & 0x3F)
			untilechunk(outBuff, inBuff, sourceOff, v12 << v51, TexelPitch)
			v48 += v12
		if ( v48 < Width ):
			v31 = v44 + 2 * ((v45 + (0xFF & (v48 >> 3))) & 3)
			v32 = v46 + (((v41 + (v48 & 7)) << (v51 + 6) >> 6) & 0xF) + 2 * ((((v41 + (v48 & 7)) << (v51 + 6) >> 6) & 0xFFFFFFF0) + (((v47 + (v48 >> 5)) << (v51 + 6)) & 0x1FFFFFFF))
			sourceOff = inBuffOffset + 8 * ((v32 & 0xFFFFFE00) + 4 * ((v31 & 0xFFFFFFFE) + 8 * (((v32 >> 6) & 7) + 8 * (v31 & 1)))) + (v32 & 0x3F)
			untilechunk(outBuff, inBuff, sourceOff, (Width - v48) << v51, TexelPitch)

def untilechunk(outBuff, inBuff, sourceOff, size, TexelPitch):
	inBuff.seek(sourceOff)
	if TexelPitch == 4:#A8R8G8B8
		data = struct.unpack(">%dL"%int(size/4), inBuff.read(size))
		outBuff.write(struct.pack("<%dL"%int(size/4), *data))
	else:
		data = inBuff.read(size)
		if TexelPitch != 1:#L8
			data = [data[(i-1) if i%2 else (i+1)] for i in range(size)]#swap every 2 bytes
			data = "".join(data)
		outBuff.write(data)
	
def parse_texture_entries(data):
	out = [0] * len(data)
	
	get = get_getter(data, ">")
	
	tex_count = get(0xC, "I")
	tex_entries = []
	
	for tex_index in xrange(tex_count):
		offset = 0x54 + 0x58 * tex_index
		width, height, mipmap, pixel_format, tex_name_off, pixel_data_off = get(offset, "IIIIII")
		
		tex_name_off += offset + 0x10
		tex_name = data[tex_name_off: data.index("\x00", tex_name_off)]
		
		tex_entries.append((width, height, pixel_format, tex_name, pixel_data_off))
	
	return tex_entries

def decode_DXT5A(data, width, height):
	get = get_getter(data, ">")
	out = [0] * (width * height)
	
	for i in xrange(height // 4):
		for j in xrange(width // 4):
			block_idx = i * (width // 4) + j
			offset = block_idx * 8
			a0, a1 = get(offset, "BB")
			index_bytes = get(offset + 0x2, "6B")
			bits = reduce(lambda x, y: x*256+y, reversed(index_bytes), 0)
			
			palette = [a0, a1]
			if a0 > a1:
				palette.extend([
					int((6*a0+1*a1)/7.0),
					int((5*a0+2*a1)/7.0),
					int((4*a0+3*a1)/7.0),
					int((3*a0+4*a1)/7.0),
					int((2*a0+5*a1)/7.0),
					int((1*a0+6*a1)/7.0),
				])
			else:
				palette.extend([
					int((4*a0+1*a1)/5.0),
					int((3*a0+2*a1)/5.0),
					int((2*a0+3*a1)/5.0),
					int((1*a0+4*a1)/5.0),
					0x0,
					0xFF,
				])
			
			for k in xrange(16):
				p = k // 4
				q = k % 4
				
				index = ((bits >> (k * 3)) & 0x7)
				out[(i * 4 + p) * width + j * 4 + q] = palette[index]
	
	return out

if __name__ == '__main__':
	tex_entry_fname = sys.argv[1]
	if len(sys.argv) >= 1 + 2:
		tex_data_fname = sys.argv[2]
	elif tex_entry_fname.endswith("8.bin"):
		tex_data_fname = tex_entry_fname.replace("8.bin", "9.bin")
	elif tex_entry_fname.endswith(".TXM"):
		tex_data_fname = tex_entry_fname.replace(".TXM", ".TXV")
	else:
		raise Exception("you need a texture entry file and a pixel data file to work!")
	
	tex_entry_data = open(tex_entry_fname, "rb").read()
	tex_entries = parse_texture_entries(tex_entry_data)
	
	for width, height, pixel_format, tex_name, pixel_data_off in tex_entries:
	
		doa_pixel_format = (pixel_format & 0xFF)
		infile = tex_data_fname
		outfile = tex_name + ".dds"
		pngfile = tex_name + ".png"
		
		untiletextures(infile, outfile, doa_pixel_format, width, height, pixel_data_off)
		
		print "tex_name: %s" % tex_name
		if doa_pixel_format != 0x7B:
			os.system(r".\script\convert %s %s" % (outfile, pngfile))			# convert dds to png(require ImageMagick)
			if doa_pixel_format != 0x54:
				os.system("del %s" % outfile)								# remove dds
		else:
			dds_data = open(outfile, "rb").read()
			dxt5a_data = dds_data[0x80:]
			alpha_data = decode_DXT5A(dxt5a_data, width, height)
			alpha_buffer = "".join(map(chr, alpha_data))
			image = Image.fromstring("L", (width, height), alpha_buffer)
			image.save(pngfile)
			os.system("del %s" % outfile)								# remove dds