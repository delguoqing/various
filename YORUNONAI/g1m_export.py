from util import log, get_getter, triangle_strip_to_list
from consts import *
import operator

def get_vertex_data_by_datatype(data, offset, datatype):
	get = get_getter(data, "<")
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

def parse_vb(g1mg, intern_state=None):
	"""
	g1mg: parsing result from parse_g1mg
	intern_state: internal state in case you want to inspect it further, dict / None
	"""

	if intern_state is None:
		intern_state = {}

	mi_list = g1mg.get("mesh_info_list")
	vb_info_list = g1mg.get("vertex_buffer_list")
	ib_list = g1mg.get("index_buffer_list")
	fvf_list = g1mg.get("fvf_list")

	if not all((mi_list, vb_info_list, ib_list)):
		return []
	print "exporting obj"
	# print mi_list

	# for j, mi in enumerate(mi_list):
	# 	vb = vb_list[mi.mesh_index]
	# 	ib = ib_list[mi.mesh_index]
	# 	print "%2d =>" % j, mi.unks0[1:], mi.unk1, mi.unk2, "mesh_index:", mi.mesh_index, ("vn:%d|%d, in:%d|%d" % (mi.vert_count, len(vb), mi.index_count, len(ib))), "vs:%d, is:%d" % (mi.vert_start, mi.index_start)
	# 	if len(vb) < mi.vert_count:
	# 		print "\tvb error"
	# 	if len(ib) < mi.index_count:
	# 		print "\tib error"
	# 	# assert j == mi.i, "testing this!!"
	# return

	# fill vb list
	vb_list = []
	has_unk = False
	for i, fvf in enumerate(fvf_list):
		# different attribute may come from different vertex buffer
		# most common case
		# for a mesh using morph animation
		# there's a vertex buffer contains position only
		# and there's another vb contains full information except that position information is all set to zero.
		log("===> fvf %d" % i, lv=0)
		vb = {}
		for offset, sematics, data_type, vb_ref_idx, vb_ref_list in fvf:
			sematic_name = SEMATIC_NAME_MAP[sematics]  # e.g. POSITION
			data_type_name = DATA_TYPE_MAP[data_type]  # e.g. float4
			fvf_size, vcount, unk2, vb_offset, vb_chunk = vb_info_list[vb_ref_list[vb_ref_idx]]
			vb[sematic_name] = []
			off = vb_offset
			for j in xrange(vcount):
				vb[sematic_name].append(get_vertex_data_by_datatype(vb_chunk, off + offset, data_type_name))
				if sematic_name == "UNK":
					has_unk = True
					tmp = vb[sematic_name][-1]
					assert math.fabs(tmp[0] ** 2 + tmp[1] ** 2 + tmp[2] ** 2 - 1.0) < 1e-3
					assert tmp[-1] == 1.0 or tmp[-1] == -1.0
				off += fvf_size
		vb_list.append(vb)

	intern_state["has_unk"] = has_unk

	return vb_list

def export_obj(g1mg):
	intern_state = {}

	vb_list = parse_vb(g1mg, intern_state=intern_state)
	if not vb_list:
		return

	mi_list = g1mg.get("mesh_info_list")
	ib_list = g1mg.get("index_buffer_list")

	text = []
	if intern_state["has_unk"]:
		text.append("# HAS UNK")

	base_i = 1
	for j, mi in enumerate(mi_list):
		text.append("o Obj%d" % j)
		text.append("s 1")
		vb = vb_list[mi.mesh_index]
		ib = ib_list[mi.mesh_index]
		print "========= %d" % j
		print str(mi)
		print "vb, size=%d" % len(vb)
		# print vb
		print "ib, size=%d" % len(ib)
		# print ib
		
		print 
		# vb = vb_list[mi.unks0[1]]
		assert len(vb["POSITION"]) >= mi.vert_count
		assert len(ib) >= mi.index_count
			
		dump_this = True or j in (1, )
		
		if dump_this:
			for i in xrange(mi.vert_start, mi.vert_start + mi.vert_count):
				x, y, z = vb["POSITION"][i]
				if "TEXCOORD0" in vb:
					u, v = vb["TEXCOORD0"][i]
					v = -v
				else:
					u, v = 0.0, 0.0
				text.append("v %f %f %f" % (x, y, z))
				text.append("vt %f %f" % (u, v))
			
			def new_face(a, b, c):
				text.append("f %d/%d %d/%d %d/%d" % (a, a, b, b, c, c))

			is_tri_strip = True
			_ib = ib[mi.index_start: mi.index_start + mi.index_count]
			index_delta = base_i - mi.vert_start
			if is_tri_strip:	# dumping tri strip
				_ib = triangle_strip_to_list(_ib, 0xFFFF)
			else:	# dumping tri_list
				assert mi.index_count % 3 == 0, "%d" % (mi.index_count % 3)
			_ib = map(lambda _idx: _idx + index_delta, _ib)
			for i in xrange(0, len(_ib), 3):
				new_face(_ib[i], _ib[i + 1], _ib[i + 2])
			if __debug__:
				min_index = min(_ib)
				max_index = max(_ib)
				print "min_index", min_index
				print "max_index", max_index

			base_i += mi.vert_count

	return "\n".join(text)

def export_gtb(g1mg, g1ms=None):
	vb_list = parse_vb(g1mg)
	if not vb_list:
		return

	mi_list = g1mg.get("mesh_info_list")
	ib_list = g1mg.get("index_buffer_list")
	mat_list = g1mg.get("material_list", [])

	gtb = {"objects": {}}

	base_i = 0
	for j, mi in enumerate(mi_list):

		vb = vb_list[mi.mesh_index]
		ib = ib_list[mi.mesh_index]
		print "========= %d" % j
		print str(mi)
		print "vb, size=%d" % len(vb)
		# print vb
		print "ib, size=%d" % len(ib)
		# print ib

		print
		# vb = vb_list[mi.unks0[1]]
		assert len(vb["POSITION"]) >= mi.vert_count
		assert len(ib) >= mi.index_count

		dump_this = True or j in (1,)

		if dump_this:

			msh = {
				"flip_v": 0, "double_sided": 0, "shade_smooth": True,
				"vertex_num": mi.vert_count, "position": [], "indices": [],
			}
			if g1ms:
				msh["max_involved_joint"] = 4
				msh["joints"] = []
				msh["weights"] = []
			else:
				msh["max_involved_joint"] = 0

			gtb["objects"]["msh%d" % j] = msh

			try:
				mat = mat_list[mi.mat_index]
			except IndexError:
				mat = None

			if mat:
				msh["textures"] = []
				uv_channels = map(operator.itemgetter(1), mat["textures"])
				uv_channels = sorted(list(set(uv_channels)))
				msh["uv_count"] = len(uv_channels)
				for i in xrange(len(uv_channels)):
					msh["uv%d" % i] = []
				for i, (tex_idx, uv_chnl_idx) in enumerate(mat["textures"]):
					msh["textures"].append((tex_idx, uv_chnl_idx))
					if i == 0:
						msh["textures"][-1] += ("diffuse", )

			for i in xrange(mi.vert_start, mi.vert_start + mi.vert_count):
				msh["position"].extend( vb["POSITION"][i] )
				for _k, uv_chnl_idx in enumerate(uv_channels):
					sematics = "TEXCOORD" + str(uv_chnl_idx)
					u, v = (sematics in vb) and (vb[sematics][i]) or (0.0, 0.0)
					msh["uv" + str(_k)].extend((u, -v))
				if msh["max_involved_joint"] > 0:
					msh["weights"].extend(vb["BLENDWEIGHTS"][i])
					msh["joints"].extend(vb["BLENDINDICES"][i])

			# dumping tri strip
			is_tri_strip = True
			_ib = ib[mi.index_start: mi.index_start + mi.index_count]
			if is_tri_strip:
				msh["indices"] = triangle_strip_to_list(_ib, 0xFFFF)
			else:	# dumping tri_list
				assert mi.index_count % 3 == 0, "%d" % (mi.index_count % 3)
				msh["indices"] = _ib
			msh["indices"] = map(lambda _idx: _idx - mi.vert_start, msh["indices"])
			msh["index_num"] = len(msh["indices"])

			if __debug__:
				min_index = min(msh["indices"])
				max_index = max(msh["indices"])
				print "min_index", min_index
				print "max_index", max_index

	if g1ms:
		skel = gtb["skeleton"] = {}
		skel["name"] = map(lambda b: b["name"], g1ms["bones"])
		skel["parent"] = map(lambda b: b["parent"] < 0 and -1 or b["parent"], g1ms["bones"])
		skel["matrix"] = []
		skel["bone_id"] = []
		for i, b in enumerate(g1ms["bones"]):
			skel["bone_id"].append(i)
			skel["matrix"].extend(b["matrix"].getA1())

	return gtb

