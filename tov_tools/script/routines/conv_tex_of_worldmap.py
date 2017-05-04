import os
import glob

os.chdir("../..")

for fname in glob.glob("./split/map/FIELD*/*.TXM") + glob.glob("./split/map/FIELD*/*/*.TXM"):
	os.system("Python script/tex_decoder.py %s" % fname)