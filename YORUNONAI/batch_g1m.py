import sys
import os
import glob
import g1m
from util import get_getter, set_log_level
from game_util import parse_bone_names_from_package_folder

ext = ".elixir"

top_folder = r"A.Land.Without.Night.JAP.PS3-ALI213/BLJM61264-[A.Land.Without.Night.JAP.PS3-ALI213]/PS3_GAME/USRDIR/Data/PS3"
chara_folder = r"A.Land.Without.Night.JAP.PS3-ALI213/BLJM61264-[A.Land.Without.Night.JAP.PS3-ALI213]/PS3_GAME/USRDIR/Data/PS3/Character"
def_root = chara_folder

input_root = len(sys.argv) > 1 and sys.argv[1] or None
root = input_root or def_root

def on_parse_end():
	# g1m.summary("unk0")
	g1m.summary_all()

def start():
	parse_count = 0
	parse_max = -1
	
	for path, dirs, files in os.walk(root):
		print "walking", path
		for fname in files:
			if fname.endswith(ext):
				folder = os.path.splitext(fname)[0]
				package_folder = os.path.normpath(os.path.join(path, folder))
				package_files = os.listdir(package_folder)
				
				# parse bone names
				bone_names = parse_bone_names_from_package_folder(
					os.path.join(package_folder, package_files[0]))
				
				for _path in package_files:
					if _path.endswith(".obj"):
						continue
					fname = os.path.join(package_folder, _path)
					f = open(fname, "rb")
					data = f.read()
					fourcc = data[:8]
					f.close()
					if fourcc == "G1M_0036":
						print "parsing %s" % fname
						# obj dump
						# g1m.dump_obj(data, fname + ".obj")
						g1m.parse(data, bone_names)
						
						parse_count += 1
						if parse_max >= 0 and parse_count >= parse_max:
							on_parse_end()
							sys.exit(0)
							
	if parse_max < 0:
		on_parse_end()
		sys.exit(0)

if __name__ == "__main__":
	set_log_level(1)
	start()