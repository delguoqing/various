import sys
import os
import glob
import decomp

ext = ".elixir.gz"
def_root = r"A.Land.Without.Night.JAP.PS3-ALI213/BLJM61264-[A.Land.Without.Night.JAP.PS3-ALI213]/PS3_GAME/USRDIR/Data/PS3"
input_root = len(sys.argv) > 1 and sys.argv[1] or None
root = input_root or def_root


for path, dirs, files in os.walk(root):
	for fname in files:
		if fname.endswith(ext):
			full_fname = os.path.join(path, fname)
			decomp.decomp(full_fname)
	