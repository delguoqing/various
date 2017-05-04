def join_mtl_files(file_names):
	mtls = set()
	for file_name in file_names:
		if file_name.endswith("all.mtl"):
			continue	
		fp = open(file_name, "r")
		mtls.add(fp.read())
		fp.close()
	fp = open("all.mtl", "w")
	for mtl in mtls:
		fp.write(mtl)
	fp.close()
	
def join_obj_files(file_names):
	lines = []
	v_base = vn_base = vt_base = 0
	
	lines.append("mtllib all.mtl\n")
	
	for file_name in file_names:
		if file_name.endswith("all.obj"):
			continue
		v = vt = vn = 0
		
		fp = open(file_name, "r")
		fp.readline()	# drop the mtllib line
		
		line = fp.readline()
		while line != "":
			if not line.startswith("f"):
				lines.append(line)
			else:
				vdata_list = line.split(" ")[1:]
				new_line = "f "
				for vdata in vdata_list:
					_v, _vt, _vn = map(int, vdata.split("/"))
					new_line += "%d/%d/%d " % (_v+v_base, _vt+vt_base, _vn+vn_base)
				lines.append(new_line + "\n")
				
			if line.startswith("v "):
				v += 1
			elif line.startswith("vn "):
				vn += 1
			elif line.startswith("vt "):
				vt += 1
			line = fp.readline()
		v_base += v
		vt_base += vt
		vn_base += vn
		fp.close()

	fp = open("all.obj", "w")
	fp.writelines(lines)
	fp.close()
	
if __name__ == '__main__':
	import glob
	join_obj_files(glob.glob("*.obj"))
	join_mtl_files(glob.glob("*.mtl"))
