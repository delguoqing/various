import os
import glob

os.chdir("../..")

for fname in glob.glob(r"./svo_unpacked/chara/*.unpacked"):
	outdir = os.path.join("./split/chara", os.path.splitext(os.path.split(fname)[1])[0])
	ret = os.system("Python script/splitter.py -f %s -o %s" % (os.path.normpath(fname), os.path.normpath(outdir)))
	if ret != 0:
		break