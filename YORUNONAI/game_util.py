import os
import sys
from util import get_getter

def parse_bone_names(path):
	f = open(path, "rb")
	data = f.read()
	f.close()
	get = get_getter(data, ">")
	
	names = []
	
	off = 0
	while off < len(data):
		str_len = get(off, "b")
		if str_len == -1:
			break
		names.append(data[off + 1: off + 1 + str_len])
		off += 1 + str_len
	return names

def parse_bone_names_from_package_folder(path):
	package_folder = os.path.split(path)[0]
	for _path in os.listdir(package_folder):
		if _path.endswith(".bin"):
			return parse_bone_names(os.path.join(package_folder, _path))
	return ()
	
def parse_bone_names_using_g1a_path(path):
	g1a_folder = os.path.split(path)[0]
	outer_folder = os.path.join(g1a_folder, "..")
	for path, dirs, files in os.walk(outer_folder):
		for fname in files:
			if fname.endswith(".bin"):
				return parse_bone_names(os.path.join(path, fname))
	return ()
	