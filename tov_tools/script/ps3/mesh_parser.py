import math
import sys
import struct
import os

TYPE_CODE = 0x00010000
HEADER_SIZE = 0x50
SHAPE_HEADER_SIZE = 0x60
EPS = 1e-5
SCALE = 0.2

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
	
	type_code = get(0x0, "I")
	assert type_code == TYPE_CODE, "this might not be a tales of versperia mesh block!"
	total_size = get(0x4, "I")
	assert total_size == len(data), "block size doesn't match, data may be corrupted!"
	
	# morph shape count?
	# there are n sub blocks in mesh file, at the end of each sub block is a
	# shape name, for example:
	#	HAIR00_RIT_C00SHAPE0
	#	POLYSURFACESHAPE23
	#	HAIR00_RIT_C00SHAPE1
	#	PCUBESHAPE4
	shape_count = get(0xC, "I")	
								
	count_unk1 = get(0x10, "I")	# count of some unknown numbers at the end of the block
	
	#name_off = get(0x14, "I")
	#name = data[name_off: data.find("\x00", name_off)]
	#print name
	
	# print out header values for later check
	for offset in xrange(0x14, HEADER_SIZE, 0x4):
		val = get(offset, "I")
		print "header values = %s" % hex(val)
	
	print "shape blocks:"
	base_offset = HEADER_SIZE
	for i in xrange(shape_count):
		print "========> shape block %d" % i
		magic_code = get(base_offset, "I")
		assert magic_code == 0x00000200, "this might not be a shape block!"
		shape_block_size = get(base_offset + 0x4, "I")
		shape_data = data[base_offset: base_offset + shape_block_size]
		
		if ref_data is not None:
			name = parse_shape(shape_data, ref_data, mat_data)
		else:
			name = parse_shape2(shape_data)

			#############
			# debug
			#############
			out_fname = "%s.shape" % name
			while os.path.exists(out_fname):
				out_fname = out_fname[:-6] + "_d.shape"		
			open(out_fname, "wb").write(shape_data)
		print "up shapename = %s" % name
		
		base_offset += shape_block_size
	
def align4(offset):
	if offset % 4 == 0:
		return offset
	return offset + (4 - offset % 4)
	
def is_normalized(normal):
	return math.fabs(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2 - 1.0) <= EPS
	
def parse_material(data):
	get = get_getter(data, ">")
	
	type_code = get(0x0, "I")
	assert type_code == 0x30000, "This may not be a Tales of Vesperia material file."
	file_size = get(0x4, "I")
	assert len(data) == file_size, "Invalid file size! This file may be corrupted!"
	version = get(0x8, "I")
	mat_count = get(0xC, "I")
	
	mat = []
	
	offset = 0xd0
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
	
def parse_shape(data, ref_data=None, mat_data=None):
	get = get_getter(data, ">")
	if mat_data is None: mat_data = []
	
	name_offset = get(0x78, "I") + 0x78
	name = get(name_offset, "%ds" % (len(data) - name_offset)).rstrip("\x00")
	
	mat_index = get(0x14, "I") - 1		# 1-based material index
	mat_count = len(mat_data)
	uv_base_off = get(0x3C, "I")
	
	name_base = name
	out_fname = name_base + ".obj"
	while os.path.exists(out_fname):
		name_base += "_d"
		out_fname = name_base + ".obj"
	mat_fname = name_base + ".mtl"
	
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
			tex_count = len(mat_data[mat_index][1])
			uv_chunk_size = 0x4 + 0x8 * tex_count
			#print mat_data
			#print hex(uv_chunk_size), hex(uv_base_off), hex(total_vcount), hex(len(ref_data)), mat_count
			for i in xrange(total_vcount):
				dummy, u, v = get_ref(uv_base_off + uv_chunk_size * i, "fff")	# use only the 1st uv
				if u > 1.0: u = math.fmod(u, 1.0)
				if u < 0.0: u = math.fmod(u, 1.0) + 1.0
				if v > 1.0: v = math.fmod(v, 1.0)
				if v < 0.0: v = math.fmod(v, 1.0) + 1.0
				fout.write("vt %f %f\n" % (u, 1-v))
				
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
		mat_f = open(mat_fname, "w")
		mat_name, tex_names = mat_data[mat_index]
		
		mat_f.write("newmtl %s\n" % mat_name)
		mat_f.write("map_Kd %s\n" % (tex_names[0] + ".png"))
		mat_f.write("\n")
		mat_f.close()
		
	return name
		
def parse_shape2(data):	
	get = get_getter(data, ">")
	
	name_offset = get(0x78, "I") + 0x78
	name = get(name_offset, "%ds" % (len(data) - name_offset)).rstrip("\x00")
	print "filename: %s.shape" % name
	
	# print out header values for later check
	for offset in xrange(0x8, SHAPE_HEADER_SIZE, 0x4):
		val = get(offset, "I")
		print "\theader values = %s" % hex(val)
		if val + offset == 0x13c:
			print "??"
		
	bone_indices = set()
	
	last_offset = 0x80 - 0xc
	for offset in xrange(0x80, len(data) - 0xc, 0x4):
		values = get(offset, "fffBBBB")
		normal = values[:3]
		_bone_indices = values[3:]
		if is_normalized(normal) and offset - last_offset >= 0xc:
			print "@offset = %s, delta=%s, %d, following=(%d,%d,%d,%d)" % ((hex(offset), hex(offset - last_offset), (offset - last_offset)/4) + _bone_indices)
			last_offset = offset
			
			for bone_index in _bone_indices:
				bone_indices.add(bone_index)
			
	# The value supposed to be color turns out to be related bone indices, one byte per bone index.
	# The vertices are grouped by related bone indices count, so may be GPU skinning is used?
	# If so, then weight infomation is contained.
	
	# If the vertex is related to n bones, then n - 1 weights are given, the last
	# weight can be computed by 1.0 - sum(all_other_weights)
	
	
	return name
	
def parse_sub7(data):
	get = get_getter(data, ">")
	
	offset = 0x0
	file_size = len(data)
	
	i = 0
	
	while offset < file_size:
		val = get(offset, "I")
		if val == 0xFFFFFFFF:
			print "vt %d @ offset %s:" % (i, hex(offset))
			i += 1
		else:
			val = get(offset, "f")
			print "\t%f" % val
		offset += 0x4
		
	
if __name__ == '__main__':
	fname = sys.argv[1]
	
	f = open(fname, "rb")
	data = f.read()
	f.close()
	
	ref_data = None
	mat_data = None
	
	# uv chunk && indices buffer file
	if len(sys.argv) >= 1 + 2:
		ref_fname = sys.argv[2]
		f = open(ref_fname, "rb")
		ref_data = f.read()
		f.close()
		
	# material entry file
	if len(sys.argv) >= 1 + 3:
		mat_fname = sys.argv[3]
		f = open(mat_fname, "rb")
		mat_data = f.read()
		f.close()
		mat_data = parse_material(mat_data)
		
	if fname.endswith(".shape"):
		parse_shape(data, ref_data)
	elif fname.endswith("7.bin") and "sub" in fname:
		parse_sub7(data)
	else:
		parse(data, ref_data, mat_data)