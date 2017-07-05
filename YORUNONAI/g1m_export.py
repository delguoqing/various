from util import log, get_getter
from consts import *

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

def export_obj(g1mg):
	mi_list = g1mg.get("mesh_info_list")
	vb_info_list = g1mg.get("vertex_buffer_list")
	ib_list = g1mg.get("index_buffer_list")
	fvf_list = g1mg.get("fvf_list")
		
	if not all((mi_list, vb_info_list, ib_list)):
		return
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
			sematic_name = SEMATIC_NAME_MAP[sematics]	# e.g. POSITION
			data_type_name = DATA_TYPE_MAP[data_type]	# e.g. float4
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

	text = []
	if has_unk:
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
				
			# dumping tri strip
			is_tri_strip = True
			if is_tri_strip:
				f = []
				rev = False
				min_index = 0x7FFFFFFF
				max_index = -1
				for i in xrange(mi.index_start, mi.index_start + mi.index_count):
					f.append(ib[i])
					min_index = min(min_index, ib[i])
					max_index = max(max_index, ib[i])
					if len(f) < 3:
						continue
					if len(f) == 4:
						f.pop(0)
					assert len(f) == 3, "invalid ib!"
					if f[-1] == 0xFFFF:
						f = []
						rev = False
					else:
						index_delta = base_i - mi.vert_start
						if not rev:
							new_face(f[0] + index_delta, f[1] + index_delta, f[2] + index_delta)
						else:
							new_face(f[2] + index_delta, f[1] + index_delta, f[0] + index_delta)
						rev = not rev
				print "min_index", min_index
				print "max_index", max_index
			else:
				assert mi.index_count % 3 == 0, "%d" % (mi.index_count % 3)
				index_delta = base_i - mi.vert_start
				for i in xrange(mi.index_start, mi.index_start + mi.index_count, 3):
					new_face(ib[i] + index_delta, ib[i + 1] + index_delta, ib[i + 2] + index_delta)
			# dumping tri_list
			base_i += mi.vert_count
	return "\n".join(text)