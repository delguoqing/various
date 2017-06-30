import sys
import os
import glob
import g1a
import util
from util import get_getter
from util import summary_all, summary
from util import log, set_log_level
ext = ".elixir"

top_folder = r"A.Land.Without.Night.JAP.PS3-ALI213/BLJM61264-[A.Land.Without.Night.JAP.PS3-ALI213]/PS3_GAME/USRDIR/Data/PS3"
chara_folder = r"A.Land.Without.Night.JAP.PS3-ALI213/BLJM61264-[A.Land.Without.Night.JAP.PS3-ALI213]/PS3_GAME/USRDIR/Data/PS3/Character"
obj_folder = r"A.Land.Without.Night.JAP.PS3-ALI213/BLJM61264-[A.Land.Without.Night.JAP.PS3-ALI213]/PS3_GAME/USRDIR/Data/PS3/Obj"
def_root = chara_folder

input_root = len(sys.argv) > 1 and sys.argv[1] or None
root = input_root or def_root

def on_parse_end():
	summary_all()
	# util.summary_save("summary_eps.bin")

def start():
	set_log_level(1)
	parse_count = 0
	parse_max = -1
	
	for path, dirs, files in os.walk(root):
		log("walking", path, lv=1)
		for fname in files:
			if fname.endswith(ext):
				folder = os.path.splitext(fname)[0]
				package_folder = os.path.normpath(os.path.join(path, folder))
				package_files = os.listdir(package_folder)
				
				for _path in package_files:
					if _path.endswith(".obj"):
						continue
					fname = os.path.join(package_folder, _path)
					f = open(fname, "rb")
					data = f.read()
					fourcc = data[:8]
					f.close()
					if fourcc == "G1A_0042":
						log("parsing %s" % fname, lv=1)
						g1a.parse(data)
						
						parse_count += 1
						if parse_max >= 0 and parse_count >= parse_max:
							on_parse_end()
							sys.exit(0)
							
	if parse_max < 0:
		on_parse_end()
		sys.exit(0)

if __name__ == "__main__":
	start()