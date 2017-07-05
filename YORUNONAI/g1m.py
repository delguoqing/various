import numpy
import struct
import os
import math
import sys
from util import get_getter, count, summary, summary_all, dump_data, log
from game_util import parse_bone_names_from_package_folder

import g1m_export

# fvf
SEMATIC_NAME_MAP = {
	0x0: "POSITION",
	0x100: "BLENDWEIGHTS",	# last weight can be computed by 1.0 - sum(BLENDWEIGHTS)
	0x200: "BLENDINDICES",
	0x300: "NORMAL",
	0x500: "TEXCOORD0",
	0x501: "TEXCOORD1",
	0x502: "TEXCOORD2",
	0x503: "TEXCOORD3",
	0x504: "TEXCOORD4",
	0x600: "PACKED(TANGENT+BINORMAL)",	# (float3+sign)
	0xa00: "COLOR0",
}

DATA_TYPE_MAP = {
	0x0: "float",
	0x100: "float2",
	0x200: "float3",
	0x300: "float4",
	0x500: "int4",
	0xd00: "RGBA"
}

class CMeshInfo(object):
	def __init__(self, mat_index, mesh_index, vert_start, vert_count, index_start,
				 index_count, unks0, unk1, unk2):
		self.mat_index = mat_index
		
		# self.i = unks0[2]	# not index!!
		self.mesh_index = mesh_index
		
		self.vert_start = vert_start
		self.vert_count = vert_count
		self.index_start = index_start
		self.index_count = index_count
	
		self.unks0 = unks0
		self.unk1 = unk1
		self.unk2 = unk2
		
	def __str__(self):
		return "\n".join([
			"buffer index: %d" % self.mesh_index,
			"material: %d" % self.mat_index,
			"vert: [%d ~ %d]" % (self.vert_start, self.vert_start + self.vert_count),
			"index: [%d ~ %d]" % (self.index_start, self.index_start + self.index_count),
			# "unks0: %r" % self.unks0,
			"unk1: %d" % self.unk1,
			"unk2: %d" % self.unk2,
			])
		
def parse(data, bone_names=()):
	ignore_chunks = set([
		"G1M_0036",
		"G1MS0032",
		"G1MM0020",
	])
	for chunk_data in iter_chunk(data):
		get = get_getter(chunk_data, ">")
		chunk_name = get(0x0, "8s")
		chunk_size = get(0x8, "I")
		##################
		# ignore chunks, for debug
		if chunk_name in ignore_chunks:
			continue
		if chunk_name.startswith("G1MG"):
			# dump_data("G1MG.bin", chunk_data)
			parse_g1mg(chunk_data)	
		elif chunk_name.startswith("G1MS"):
			parse_g1ms(chunk_data, bone_names=bone_names)
		elif chunk_name.startswith("G1MM"):
			parse_g1mm(chunk_data)

def dump_obj(data, out_path):
	obj_text = ""
	for chunk_data in iter_chunk(data):
		get = get_getter(chunk_data, ">")
		chunk_name = get(0x0, "8s")
		chunk_size = get(0x8, "I")
		if chunk_name.startswith("G1MG"):
			g1mg = parse_g1mg(chunk_data)
			obj_text = g1m_export.export_obj(g1mg)
			break
	if obj_text:
		fout = open(out_path, "w")
		fout.write(obj_text)
		fout.close()
	return None

def iter_chunk(data):
	get = get_getter(data, ">")
	
	fourcc = get(0x0, "8s")
	assert fourcc == "G1M_0036", "invalid g1m file!"
	
	filesize = get(0x8, "I")
	assert filesize == len(data), "file size not match, file may be corrupted!"
	
	headersize = get(0xc, "I")	# usually the 1st chunk offset
	unk = get(0x10, "I")
	assert unk == 0x0, "this may not be a reserved field!"
	chunk_count = get(0x14, "I")	# usually 5 chunks but not always
	
	off = headersize
	for i in xrange(chunk_count):
		chunk_name = get(off, "8s")
		chunk_size = get(off + 0x8, "I")
		
		print "chunk: %s, size: 0x%x" % (chunk_name, chunk_size)
		chunk_data = data[off: off + chunk_size]
		yield chunk_data
		off += chunk_size
	
	assert off == filesize, "invalid file size not match!!"

def iter_g1mg_subchunk(data):
	get = get_getter(data, ">")
	chunk_name = get(0x0, "8s")
	chunk_size = get(0x8, "I")
	platform = get(0xc, "4s")
	assert platform == "PS3\x00", "platform error!"
	unk = get(0x10, "I")
	assert unk == 0x0, "null padding value!"
	bbox = get(0x14, "6f")	# (xmin, ymin, zmin, xmax, ymax, zmax)
	print "bounding box:", bbox
	schunk_count = get(0x2c, "I")
	off = 0x30
	for i in xrange(schunk_count):
		schunk_type, schunk_size = get(off, "2I")
		yield data[off: off + schunk_size]
		off += schunk_size

def get_g1mg_subchunk_data(data, schunk_type):
	for chunk_data in iter_chunk(data):
		get = get_getter(chunk_data, ">")
		chunk_name = get(0x0, "8s")
		chunk_size = get(0x8, "I")
		if chunk_name.startswith("G1MG"):
			for subchunk_data in iter_g1mg_subchunk(chunk_data):
				sub_get = get_getter(subchunk_data, ">")
				if sub_get(0x0, "I") == schunk_type:
					return subchunk_data
			return None

def parse_g1mg_subchunk_0x10001(schunk_data):
	dump_chunk = True
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	entry_count = get(0x8, "I")
	reserved = get(0xc, "I")
	assert reserved == 0x100
	assert len(schunk_data) == 0x10 + entry_count * 0x40
	log("entry_count=%d" % entry_count, lv=0)
	# entry size == 0x40, but not matrix	
	if dump_chunk:
		dump_data("g1mg_0x10001.bin", schunk_data)

# mat
def parse_g1mg_subchunk_0x10002(schunk_data):
	log("========", lv=1)
	log("materials", lv=1)
	log("========", lv=1)
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	mat_count = get(0x8, "I")
	# dump_data("g1mg_0x10002.bin", schunk_data)
	off = 0xc
	for mat_idx in xrange(mat_count):
		unk0 = get(off + 0x0, "I")
		assert unk0 == 0
		tex_count = get(off + 0x4, "I")
		unk1, unk2 = get(off + 0x8, "Ii")
		unk1_equal_tex_count = tex_count == unk1
		count(locals(), "unk1_equal_tex_count")
		log("mat %d, tex_count %d, unk1=%d, unk2=%d, unk1_equal_tex_count=%d" % (mat_idx, tex_count, unk1, unk2, unk1_equal_tex_count), lv=1)
		assert 1 <= unk1 <= 7
		assert unk2 == 1 or unk2 == -1
		off += 0x10
		for tex_idx in xrange(tex_count):
			tex_identifier = get(off + 0x0, "H")
			uv_chnl_idx, unk6 = get(off + 0x2, "HH")
			unk3, unk4, unk5 = get(off + 0x6, "3H")
			count(locals(), "unk6")
			assert 0 <= unk3 <= 2
			assert unk4 == 4
			assert unk5 == 4
			assert 0 <= uv_chnl_idx <= 4, "works for this game!"
			off += 0xc
			log("tex_idx = %d, uv_channel_idx = %d, unk6 = %d, unk3 = %d, unk4 = %d, unk5 = %d" % (tex_identifier, uv_chnl_idx, unk6, unk3, unk4, unk5), lv=1)
	log("")

# uniforms
def parse_g1mg_subchunk_0x10003(schunk_data):
	log("================", lv=0)
	log("uniforms", lv=0)
	log("================", lv=0)
	dump_chunk = False
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	uniform_blk_cnt = get(0x8, "I")
	offset = 0xc
	for uniform_blk_idx in xrange(uniform_blk_cnt):
		uniform_cnt = get(offset + 0x0, "I")
		log("\nuniform block %d: uniform_num=%d" % (uniform_blk_idx, uniform_cnt), lv=0)
		offset += 0x4
		for uniform_idx in xrange(uniform_cnt):
			tot_len, name_len = get(offset, "2I")
			reserved0, datatype, reserved1 = get(offset + 0x8, "I2H")
			assert reserved0 == 0 and reserved1 == 1
			name = get(offset + 0x10, "%ds" % name_len).rstrip("\x00")
			rem_size = tot_len - 0x10 - name_len
			if 1 <= datatype <= 4:
				vec_size = datatype
				assert rem_size == vec_size * 0x4
				values = get(offset + 0x10 + name_len, "%df" % vec_size, force_tuple=True)
				values_string = ",".join(["%.4f" % v for v in values])
			elif datatype == 5:
				assert rem_size == 4
				values = get(offset + 0x10 + name_len, "4B", force_tuple=True)
				values_string = ",".join(["%d" % v for v in values])
			else:
				assert False
			log("\tuniform: %s, values=%s, datatype=%d" % (name, values_string, datatype), lv=0)
			offset += tot_len
			
	if dump_chunk:
		dump_data("g1mg_0x10003.bin", schunk_data)
	
# vb
def parse_g1mg_subchunk_0x10004(schunk_data):
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	mesh_seg_count = get(0x8, "I")
	off = 0xc
	
	vertex_buffer_list = []
	
	for j in xrange(mesh_seg_count):
		unk1, fvf_size, vcount, unk2 = get(off, "4I")
		print "%d => mesh segment @ offset=0x%x, vcount=%d, fvf_size=0x%x, unk1=%d, unk2=%d" % (j, off, vcount, fvf_size, unk1, unk2)
		assert unk1 == 0 and (unk2 == 0 or unk2 == 1), "unknown values!!"
		vertex_buffer = (fvf_size, vcount, unk2, off + 0x10, schunk_data)
		vertex_buffer_list.append(vertex_buffer)
		off += 0x10 + vcount * fvf_size
	return {"vertex_buffer_list": vertex_buffer_list}

# fvf (fully parsed)
def parse_g1mg_subchunk_0x10005(schunk_data):
	fvf_list = []
	
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	fvf_count = get(0x8, "I")
	log("fvf count", fvf_count, lv=0)
	off = 0xc
	tot_vb_ref_list = []
	for i in xrange(fvf_count):
		log("fvf %d" % i, lv=0)
		vb_ref_count = get(off + 0x0, "I")
		vb_ref_list  = get(off + 0x4, "%dI" % vb_ref_count, force_tuple=True)
		tot_vb_ref_list.extend(vb_ref_list)
		attr_count = get(off + 0x4 + vb_ref_count * 0x4, "I")
		log("off = 0x%x, attr_count: %d, vb_ref_list:" % (off, attr_count), vb_ref_list, lv=0)
		off += 0x8 + vb_ref_count * 0x4
		attrs = []
		for j in xrange(attr_count):
			vb_ref_idx, offset    = get(off + 0x0, "2H")
			assert 0 <= vb_ref_idx < vb_ref_count
			data_type = get(off + 0x4, "H")
			sematics  = get(off + 0x6, "H")
			log("\tvb_ref_idx=%d, off=0x%x, datatype=0x%x__%s, sematics=0x%x__"\
				"%s" % (vb_ref_idx, offset, data_type,
									 DATA_TYPE_MAP.get(data_type, "_UNK_"), sematics,
									 SEMATIC_NAME_MAP.get(sematics, "_UNK_")), lv=0)
			off += 0x8
			attrs.append((offset, sematics, data_type, vb_ref_idx, vb_ref_list))
		fvf_list.append(attrs)
	assert tot_vb_ref_list == range(len(tot_vb_ref_list))
	return {"fvf_list": fvf_list}

# joint mapping?
def parse_g1mg_subchunk_0x10006(schunk_data):
	dump_chunk = False
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	entry_count = get(0x8, "I")
	off = 0xc
	log("entry_count=%d" % entry_count, lv=0)
	for entry_idx in xrange(entry_count):
		item_count = get(off, "I")
		mat_ref_idx, unk0, unk1, unk2, joint_map_idx = get(off + 0x4, "IHHHH")
		assert unk0 == 0x8000 and unk2 == 0x8000
		#count(locals(), "unk1")
		off += 0x4 + item_count * 0xc
	assert off == len(schunk_data)
	if dump_chunk:
		dump_data("g1mg_0x10006.bin", schunk_data)
		
# ib
def parse_g1mg_subchunk_0x10007(schunk_data):
	print "index buffer block"
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	ib_count = get(0x8, "I")
	off = 0xc
	index_buffer_list = []
	for j in xrange(ib_count):
		index_count, b, c = get(off, "3I")
		try:
			index_buffer_list.append(get(off + 0xc, "%dH" % index_count))
		except struct.error, e:
			dump_data("g1mg_0x10007.bin", schunk_data)
			raise e
		off += 0xc + index_count * 2		
			
		print "%d => index_count: %d, 0x%x" % (j, index_count, b)
	# print off, schunk_size
	assert off == schunk_size, "sub chunk size not match!! 0x%x vs 0x%x" % (off, schunk_size)
	return {"index_buffer_list": index_buffer_list}
	
# mesh
def parse_g1mg_subchunk_0x10008(schunk_data):
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	print "mesh block:"
	mesh_count = get(0x8, "I")
	# if mesh_count > 0:
	# 	dump_data("g1mg_0x10008.bin", schunk_data)
	# 	raise sys.exit(0)
	off = 0xc
	mesh_info_list = []
	for i in xrange(mesh_count):
		unks0 = get(off, "2H5I")
		mat_index, mesh_index, unk1, unk2, vert_start, vert_count, index_start, index_count \
			= get(off + 6*4, "8I")
		mesh_info = CMeshInfo(mat_index, mesh_index, vert_start, vert_count, index_start,
							  index_count, unks0, unk1, unk2)
		# assert unks0[3] == i # wrong
		print i, "=>", "0x%x, 0x%x, %d, %d, %d, %d, uniform_idx:%d, mat_idx:%d, mesh_idx:%d, %d, %d, vert_start:%d, vert_count:%d, index_start:%d, index_count: %d" % get(off, "2H13I")
		mesh_info_list.append(mesh_info)
		off += 0x38
	return {"mesh_info_list": mesh_info_list}
	
def parse_g1mg_subchunk_0x10009(schunk_data):
	get = get_getter(schunk_data, ">")
	schunk_type, schunk_size = get(0x0, "2I")
	unk0 = get(0x8, "I")
	assert unk0 == 1 or unk0 == 2
	reserved = get(0xc, "3I")
	assert not any(reserved)
	shader_count1, shader_count2 = get(0x18, "II")
	
	dump_data("g1mg_0x10009.bin", schunk_data)
	off = 0x28
	print "1st block shader:"
	for shader_idx in xrange(shader_count1):
		unk1 = get(off, "I")
		# assert unk1 == 0xFFFFFFFF
		unk_cnt = get(off + 0x4, "I")
		off += 0x8 + unk_cnt * 0x4
		shader_name = get(off, "16s").rstrip("\x00")
		off += 0x10
		unk_2, unk3 = get(off, "2H")
		off += 0x4 + unk_2 * 0x2
		print "\tshader:", shader_name
	# print "2nd block shader:"
	# for shader_idx in xrange(shader_count2):
	# 	unk1 = get(off, "I")
	# 	# assert unk1 == 0xFFFFFFFF
	# 	unk_cnt = get(off + 0x4, "I")
	# 	off += 0x8 + unk_cnt * 0x4
	# 	shader_name = get(off, "16s").rstrip("\x00")
	# 	off += 0x10
	# 	unk_2, unk3 = get(off, "2H")
	# 	off += 0x4 + unk_2 * 0x2
	# 	print "\tshader:", shader_name		

# g = geometry
def parse_g1mg(data):
	g1mg = {}
	for schunk_data in iter_g1mg_subchunk(data):
		get = get_getter(schunk_data, ">")
		schunk_type, schunk_size = get(0x0, "2I")
		
		print "chunk_type=0x%x, chunk_size=0x%x" % (schunk_type, schunk_size)
		
		assert schunk_type in xrange(0x10001, 0x1000A), "not recognized schunk type !! 0x%x" % schunk_type
		handler = G1MG_SUBCHUNK_HANDLER.get(schunk_type)
		if handler is None:
			continue
		ret = handler(schunk_data)
		if ret is not None:
			g1mg.update(ret)
	return g1mg
	
# s = skeleton
def parse_g1ms(data, bone_names=()):
	get = get_getter(data, ">")
	fourcc = get(0x0, "8s")
	assert fourcc == "G1MS0032", "invalid g1ms chunk"
	g1ms_size = get(0x8, "I")
	assert g1ms_size == len(data), "invalid g1ms size"
	bone_info_offset = get(0xc, "I")
	
	unk0 = get(0x10, "I")
	assert unk0 in (0, 0x80000000)	# 0x0 		 -- dummy skeleton
									# 0x80000000 -- normal skeleton
									# unk0 is probably a float (0.0 or -0.0)

	bone_count = get(0x14, "H")
	bone_slot_count = get(0x16, "H")
	
	reserved0 = get(0x18, "H")
	assert reserved0 == 0x1
	reserved1 = get(0x1a, "H")
	assert reserved1 == 0x0

	bone_indices = get(0x1c, "%dh" % bone_slot_count, force_tuple=True)
	assert list(bone_indices[:bone_count]) == range(bone_count)
	assert bone_indices[bone_count:] == (-1, ) * (bone_slot_count - bone_count)

	max_bone_index = get(0x1c + bone_slot_count * 2, "h")
	assert max_bone_index == bone_count - 1

	off = bone_info_offset
	for i in xrange(bone_count):
		scale = get(off, "3f")
		parent = get(off + 0xc, "i")
		rot = get(off + 0x10, "4f")
		pos = get(off + 0x20, "4f")
		
		if bone_names:
			# print bone_names, parent
			if parent < 0:
				assert parent in (-1, -2147483648), "whatever"
				parent_name = "nil"
			else:
				parent_name = bone_names[parent]
			my_name = bone_names[i]
		else:
			my_name = parent_name = ""
			
		print "bone %d: %s; parent %d: %s" % (i, my_name, parent, parent_name)
		print "scale: (%f, %f, %f)" % scale
		print "rot : (%f, %f, %f, %f)" % rot
		print "pos : (%f, %f, %f, %f)" % pos
		assert math.fabs(rot[0] ** 2 + rot[1] ** 2 + rot[2] ** 2 + rot[3] ** 2 - 1.0) < 0.01
		assert math.fabs(pos[-1] - 1.0) < 0.01
		off += 0x30
	
def get_vertex_data_by_datatype(data, offset, datatype):
	get = get_getter(data, ">")
	if datatype == "float":
		return get(offset, "f")
	elif datatype == "float2":
		return get(offset, "2f")
	elif datatype == "float3":
		return get(offset, "3f")
	elif datatype == "float4":
		return get(offset, "4f")
	elif datatype == "int4":
		return get(offset, "4B")
	elif datatype == "RGBA":
		return hex(get(offset, "I"))
	assert False, "impossible"
			
G1MG_SUBCHUNK_HANDLER = {
	# 0x10001: parse_g1mg_subchunk_0x10001,
	0x10002: parse_g1mg_subchunk_0x10002,	# material
	0x10003: parse_g1mg_subchunk_0x10003,	# uniform
	0x10004: parse_g1mg_subchunk_0x10004,	# vb
	0x10005: parse_g1mg_subchunk_0x10005,	# fvf
	# 0x10006: parse_g1mg_subchunk_0x10006,
	0x10007: parse_g1mg_subchunk_0x10007,	# ib
	0x10008: parse_g1mg_subchunk_0x10008,	# mesh
	0x10009: parse_g1mg_subchunk_0x10009,	# shader
}
# debug
# G1MG_SUBCHUNK_HANDLER = {
#  	0x10009: parse_g1mg_subchunk_0x10009,
# }
# matrices
def parse_g1mm(data):
	get = get_getter(data, ">")
	fourcc = get(0x0, "8s")
	assert fourcc == "G1MM0020", "invalid fourcc!!"
	chunk_size = get(0x8, "I")
	assert chunk_size == len(data), "ok"
	mat_count = get(0xc, "I")
	for i in xrange(mat_count):
		mat = get(0x10 + 0x40 * i, "16f")
		for j in xrange(4):
			print mat[j * 4: (j + 1) * 4]

if __name__ == '__main__':
	f = open(sys.argv[1], "rb")
	data = f.read()
	f.close()
	
	bone_names = parse_bone_names_from_package_folder(sys.argv[1])
	
	print "bone_names count: %d" % len(bone_names)
	# dump_obj(data, sys.argv[1] + ".obj")
	parse(data, bone_names)
	