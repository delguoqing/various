import sys
import os
import glob
import g1t
from consts import G1TG0060

ext = ".elixir"
def_root = r"A.Land.Without.Night.JAP.PS3-ALI213/BLJM61264-[A.Land.Without.Night.JAP.PS3-ALI213]/PS3_GAME/USRDIR/Data/PS3"
input_root = len(sys.argv) > 1 and sys.argv[1] or None
root = input_root or def_root

for path, dirs, files in os.walk(root):
	print "walking", path
	for fname in files:
		if fname.endswith(ext):
			folder = os.path.splitext(fname)[0]
			package_folder = os.path.normpath(os.path.join(path, folder))
			for _path in os.listdir(package_folder):
				fname = os.path.join(package_folder, _path)
				f = open(fname, "rb")
				data = f.read()
				fourcc = data[:8]
				f.close()
				if fourcc == G1TG0060:
					print "parsing %s" % fname
					g1t.tex_extract(fname)
