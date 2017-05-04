import math
import sys
import struct
import os
import argparse

PLATFORM_X360 = 0x4

TYPE_CODE = 0x00010000
HEADER_SIZE = 0x50
SHAPE_HEADER_SIZE = 0x60
EPS = 1e-5
SCALE = 0.2

# flags of each shape, long@0x18:
# 0x72: no bone weights, store vertex data in external file.
# 0xF2: have bone weights, store vertex data in separate files.
# 0xF3: ?
# 0x2F2: no bone weights, store vertex data in separate files.
FLAG_EXTERNAL_VERTEX = 0x72
FLAG_SET = set([0x72, 0X71, 0x70, 0xF2, 0xF1, 0xF3, 0x2F2, 0x272])

# makes parsing data a lot easier
def get_getter(data, endian):
	def get(offset, fmt):
		size = struct.calcsize(fmt)
		res = struct.unpack(endian + fmt, data[offset: offset + size])
		if len(res) == 1:
			return res[0]
		return res
	return get


def parse(data, ref_data=None, mat_data=None):
	get = get_getter(data, ">")

	# mesh header parse
	# header size = 0x50
	type_code = get(0x0, "I")
	assert type_code == TYPE_CODE, "this might not be a tales of versperia mesh block!"
	total_size = get(0x4, "I")
	assert total_size == len(data), "block size doesn't match, data may be corrupted!"
	
	# platform(?) == 0x3 in chara/AHOC/NONAME2/KK_BAG_HUM_C022
	#					 in chara/AHOC/NONAME2/KK_BELT_HUM_C022
	#					 in chara/APE_C/NONAME2/KK_BAG00_SHP
	#					 in chara/APE_C/NONAME2/KK_GLASSES_KAU_C000
	
	platform = get(0x8, "I")
	assert platform in (PLATFORM_X360, 0x3, 0x2), "this file is not from x360 version!"
	if platform != PLATFORM_X360:
		print "=========> WARNING: platform == 0x%x!!!!!!!!" % platform
		
	# shape(sub mesh) count
	# there are n sub blocks in one mesh file, at the end of each sub block is a
	# shape name, for example:
	#	HAIR00_RIT_C00SHAPE0
	#	POLYSURFACESHAPE23
	#	HAIR00_RIT_C00SHAPE1
	#	PCUBESHAPE4	
	shape_count = get(0xC, "I")
	bone_count = get(0x10, "I")
	bone_info_off = get(0x14, "I")
	# There're 3 kind of extra blocks in the file.
	offset = 0x18
	for i in xrange(3):
		extra_block_off, extra_block_n = get(offset, "2I")
		if extra_block_n > 0:
			parse_extra_block(i, data, offset + extra_block_off)
		offset += 0x8
	string_table_off_for_extra_block = get(offset, "I")
	offset += 0x4
	
	# padding header to size 0x50 or unknown fields
	zeros = get(offset, "7I")
	assert not any(zeros), "hey you need check this. Have something unknown!"
	
	# shape blocks paring
	print "shape blocks:"
	base_offset = HEADER_SIZE
	for i in xrange(shape_count):
		print "========> shape block %d @off=0x%x" % (i, base_offset)
		magic_code = get(base_offset, "I")
		assert magic_code == 0x00000200, "this might not be a shape block!"
		shape_block_size = get(base_offset + 0x4, "I")
		shape_index = get(base_offset + 0x8, "I")
		#assert i == shape_index - 1, "is not shape index!!"
		shape_data = data[base_offset: base_offset + shape_block_size]
		
		if ref_data is not None:
			name = parse_shape(shape_data, ref_data, mat_data)

		base_offset += shape_block_size
		
def align4(offset):
	if offset % 4 == 0:
		return offset
	return offset + (4 - offset % 4)
	
def is_normalized(normal):
	return math.fabs(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2 - 1.0) <= EPS
	
def parse_material(data):
	get = get_getter(data, ">")
	
	mat_count = get(0xC, "I")
	
	mat = []
	
	offset = 0x50
	for mat_index in xrange(mat_count):
		mat_size = get(offset + 0x4, "I")
		
		mat_name_off = get(offset + 0x8, "I")
		mat_name_off += offset + 0x8
		mat_name = data[mat_name_off: data.index("\x00", mat_name_off)]
		
		tex_count = get(offset + 0x64, "I")
		tex_names = []
		for tex_index in xrange(tex_count):
			tex_name_off = get(offset + 0x68 + tex_index * 0x4, "I")
			tex_name_off += offset + 0x68 + tex_index * 0x4
			tex_name = data[tex_name_off: data.index("\x00", tex_name_off)]
			tex_names.append(tex_name)
	
		mat.append((mat_name, tex_names))
		
		offset += mat_size
	return mat
	
def is_vertex_data_external(flag):
	return (flag & 0xF0) == 0x70
	
def fix_uv(uv):
	u, v = uv
	# wrong
	#if u > 1.0: u = math.fmod(u, 1.0)
	#if u < 0.0: u = math.fmod(u, 1.0) + 1.0
	#if v > 1.0: v = math.fmod(v, 1.0)
	#if v < 0.0: v = math.fmod(v, 1.0) + 1.0
	#return u, 1.0 - v
			
	# right
	return u, 1.0 - v
	
def parse_shape(data, ref_data=None, mat_data=None):
	get = get_getter(data, ">")
	if mat_data is None: mat_data = []
	
	dup_idx = get(0xc, "I")
	unk_0x10 = get(0x10, "I")

	name_offset = get(0x78, "I") + 0x78
	name_end_offset = get(0x80, "I") + 0x80
	
	name = get(name_offset, "%ds" % (len(data) - name_offset)).rstrip("\x00")
	assert (name == data[name_offset: name_end_offset - 1]), "not shape name end offset!!!"

	assert unk_0x10 == 0, "shape: %s, unknown nonzero value!" % name
	
	mat_index = get(0x14, "I") - 1		# 1-based material index
	mat_count = len(mat_data)
	ex_data_off = get(0x3C, "I")	# external vertex data offset
	
	name_base = name
	if dup_idx != 0:
		name_base += "_%d" % dup_idx
	out_fname = name_base + ".obj"
	
	mat_fname = name_base + ".mtl"
	out_fname = out_fname.replace(":", "_")
	mat_fname = mat_fname.replace(":", "_")
	
	fout = open(out_fname, "w")
	
	if ref_data is not None and mat_count > 0:
		fout.write("mtllib %s\n" % mat_fname)
		fout.write("usemtl %s\n" % mat_data[mat_index][0])
	fout.write("s 1\n")
	
	#fout = sys.stdout
	#print "filename: %s.shape" % name
	
	# print out header values for later check
	for offset in xrange(0x8, SHAPE_HEADER_SIZE, 0x4):
		val = get(offset, "I")
		#print "\theader values = %s" % hex(val)
		
	size = get(0x80, "I") + 0x80
	#assert align4(size + 1) == len(data), "file size not match!!! %s v.s %s" % (hex(size), hex(len(data)))
	
	total_vcount = get(0x20, "I")
	bcount_2_vcount = {}
	for i, offset in enumerate(xrange(0x24, 0x34, 0x4)):
		bcount_2_vcount[i+1] = get(offset, "I")
	bcount_2_vcount[0] = total_vcount - sum(bcount_2_vcount.values())
	assert total_vcount >= sum(bcount_2_vcount.values()), "vertex number don't match!"
	
	bone_indices = set()
	normals_list = []
	
	flag = get(0x18, "I")
	assert flag in FLAG_SET, "Unknown flag!! flag = 0x%x" % flag
	external_size = get(0x1c, "I")
	
	uv_channel_count = (flag & 0x3)
	
	print "flag = 0x%x, external size = 0x%x" % (flag, external_size)
	print "bcount_2_vcount", bcount_2_vcount
	print "index @0x%x, count=%d" % (get(0x40, "I"), get(0x34, "I"))
	print "ex data off@0x%x" % (ex_data_off)
	# for some models, vertex data are separate in two streams.
	# for other models, they are stored together.
	if is_vertex_data_external(flag):
		offset = ex_data_off
		get_ref = get_getter(ref_data, ">")
		
		for _ in xrange(total_vcount):
			if external_size in (0x24, 0x2C):
				positions = get_ref(offset, "fff")
				fout.write("v %f %f %f\n" % positions)
			
				normals = get_ref(offset + 0xc, "fff")
				normals_list.append(normals)
			elif external_size in (0x1C, ):
				positions = get_ref(offset, "3f")
				fout.write("v %f %f %f\n" % positions)

				normals = get_ref(offset + 0xc, "fff")
				normals_list.append(normals)
			else:
				assert False, "unknown external data size! flag=0x%x, size=0x%x" % (flag, external_size)
			offset += external_size
			
	else:
		# This offset may not be correct!
		offset = 0x84
		for bone_count in xrange(0, 4+1, 1):
			vcount = bcount_2_vcount[bone_count]
			
			fout.write("\n# vertices with %d control bones: %d, offset=%s\n" % (bone_count, vcount, hex(offset)))
			
			for _ in xrange(vcount):
				positions = get(offset, "fff")
				fout.write("v %f %f %f\n" % positions)
				offset += 0xc
			
				normals = get(offset, "fff")
				normals_list.append(normals)
				offset += 0xc
				
				if bone_count > 0:	
					_bone_indices = get(offset, "BBBB")
					offset += 0x4
				
					bone_indices.update(_bone_indices)
				
				if bone_count > 1:
					weights = get(offset, "f"*(bone_count-1))
					offset += 0x4 * (bone_count-1)
					if bone_count - 1 == 1:
						weights = [weights]
					else:
						weights = list(weights)
				else:
					weights = []
				weights.append(1.0 - sum(weights))
			
				assert weights[-1] > 0, "sum of given weights should not exceed 1.0"
				#assert is_normalized(normals), "should be normalized!! %r" % (normals, )
	
		#print bone_indices
		assert offset == name_offset, "data remaining!!"
	
	for normals in normals_list:
		fout.write("vn %f %f %f\n" % normals)
	
	if ref_data is not None:
		indices_offset = get(0x40, "I")
		indices_count = get(0x34, "I")
		get_ref = get_getter(ref_data, ">")
		
		if mat_count > 0:
			uv_chunk_size = external_size
			#print mat_data
			#print hex(uv_chunk_size), hex(ex_data_off), hex(total_vcount), hex(len(ref_data)), mat_count
			for i in xrange(total_vcount):
				if external_size == 0x14:
					color, u, v = get_ref(ex_data_off + uv_chunk_size * i, "fff")	# use only the 1st uv
				else:
					u, v = get_ref(ex_data_off + uv_chunk_size * i + 0x1C, "ff")
				u, v = fix_uv((u, v))
				fout.write("vt %f %f\n" % (u, v))
					
		indices = get_ref(indices_offset, "%dH" % indices_count)
		
		write_group = False
		group_idx = 1
		
		for i in xrange(indices_count - 2):
			a, b, c = indices[i: i + 3]
			is_new_group = (i == 0 or a == 0xFFFF)
			write_face = not (0xFFFF in (a, b, c))
			
			if is_new_group:
				fout.write("# group @offset=0x%x\n" % (indices_offset + i * 0x2))
				if write_group:
					fout.write("g g%d\n" % group_idx)
				group_idx += 1
				clockwize = True
				
			if write_face:
				if clockwize:
					fout.write("f %d/%d/%d %d/%d/%d %d/%d/%d\n" % (a+1, a+1, a+1, b+1, b+1, b+1, c+1, c+1, c+1))
				else:
					fout.write("f %d/%d/%d %d/%d/%d %d/%d/%d\n" % (c+1, c+1, c+1, b+1, b+1, b+1, a+1, a+1, a+1))
				clockwize = not clockwize
					
	if mat_count > 0:
		mat_f = open(mat_fname.replace(":", "_"), "w")
		mat_name, tex_names = mat_data[mat_index]
		
		mat_f.write("newmtl %s\n" % mat_name)
		if tex_names:	# There're materials without texture
			mat_f.write("map_Kd %s\n" % (tex_names[0] + ".png"))
		mat_f.write("\n")
		mat_f.close()
		
	return name

def parse_extra_block_type2_old(data, str_tab, str_tab_off):
	get = get_getter(data, ">")
	file_type = get(0x0, "I")
	assert file_type == 0x230, "this is not a extra block type 2!"
	file_size = get(0x4, "I")
	assert len(data) == file_size, "invalid file! file size not match!"
	mat_index = get(0xC, "I") - 1
	shape_name_off = get(0x10, "I") + 0xC - str_tab_off
	shape_name = str_tab[shape_name_off: str_tab.find("\x00", shape_name_off)]
	vertex_count = get(0x14, "I")
	
	# obj format don't support vertex color
	# extra block type2 has no index buffer ?
	pos_list = []
	uv_list = []
	for offset in xrange(0x58, 0x58 + 0x18 * vertex_count, 0x18):
		print hex(offset)
		x, y, z, color, u, v = get(offset, "fffIff")
		pos_list.append((x, y, z))
		uv_list.append(fix_uv((u, v)))
	
	for (x, y, z) in pos_list:
		print "v %f %f %f" % (x, y, z)
	for (u, v) in uv_list:
		print "vt %f %f" % (u, v)
	
	# v/vt/vn
	tri_count = vertex_count - 2
	clockwize = True
	for i in xrange(tri_count):
		if clockwize:
			a, b, c = i, i + 1, i + 2
		else:
			a, b, c = i + 2, i + 1, i
		clockwize = not clockwize
		print "f %d/%d %d/%d %d/%d" % (a+1, a+1, b+1, b+1, c+1, c+1)

def parse_extra_blocks(type_id, data, offset, n):
	get = get_getter(data, ">")
	if type_id == 1:
		for i in xrange(n):
			block_size = get(offset + 0x4, "I")
			block_data = data[offset: offset + block_size]
			parse_extra_block_type1(block_data)
			offset += block_size
	else:
		assert False, "not support such extra block type!!! %d" % type_id

def parse_extra_block_type1(data):
	get = get_getter(data, ">")
	
	type_code = get(0x0, "I")
	assert type_code == 0x220, "incorrect type code!!"
	
	block_size = get(0x4, "I")
	assert block_size == len(data), "incorrect block size!!"
	
# Local Bone Id to Global Bone Id
# Local Bone Id: bone id used in this mesh.
# Global Bone Id: bone id shared by all models.
# Related Knowledge: animation retargeting
def get_loc_bid_to_glb_bid(data):
	get = get_getter(data, ">")
	count, offset = get(0x10, "2I")
	offset += 0x14
	raw = get(offset, "%dI" % count)
	loc2glb = {}
	for locbid, glbbid in enumerate(raw):
		loc2glb[locbid] = glbbid
	return loc2glb
	
if __name__ == '__main__':
	fname = sys.argv[1]
	
	f = open(fname, "rb")
	data = f.read()
	f.close()
	
	# resolve reference filenames
	if fname.endswith(".SPM"):
		ref_fname = fname.replace(".SPM", ".SPV")
		mat_fname = fname.replace(".SPM", ".MTR")
	else:
		ref_fname = sys.argv[2]
		mat_fname = sys.argv[3]
	
	# uv chunk && indices buffer file
	f = open(ref_fname, "rb")
	ref_data = f.read()
	f.close()
		
	# material entry file
	f = open(mat_fname, "rb")
	mat_data = f.read()
	f.close()
	mat_data = parse_material(mat_data)
		
	parse(data, ref_data, mat_data)