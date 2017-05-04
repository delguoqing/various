import os
import glob

os.chdir("../..")
print os.getcwd()

for fname in glob.glob("./svo_unpacked/map/*.unpacked"):
	outdir = os.path.join("./split/map", os.path.splitext(os.path.split(fname)[1])[0])
	ret = os.system("Python script/splitter.py -f %s -o %s" % (fname, outdir))
	if ret != 0:
		break