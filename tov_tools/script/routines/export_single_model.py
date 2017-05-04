import os
import sys

def export_all_weapons():
	import glob
	for fin in glob.glob("../effect_rip/unpacked/W_*.unpacked"):
		fout = os.path.join("./weapons/", os.path.split(fin)[1][:-9])
		export_one_model(fin, fout)

def export_yuri_weapons():
	import glob
	for fin in glob.glob("../effect_rip/unpacked/W_SWO_Y_*.unpacked"):
		fout = os.path.join("./weapons/", os.path.split(fin)[1][:-9])
		export_one_model(fin, fout)
	for fin in glob.glob("../effect_rip/unpacked/W_AXE_Y_*.unpacked"):
		fout = os.path.join("./weapons/", os.path.split(fin)[1][:-9])
		export_one_model(fin, fout)		

def export_judith_weapons():
	import glob
	for fin in glob.glob("../effect_rip/unpacked/W_LEG_J_*.unpacked"):
		fout = os.path.join("./weapons/", os.path.split(fin)[1][:-9])
		export_one_model(fin, fout)
	for fin in glob.glob("../effect_rip/unpacked/W_CLU_J_*.unpacked"):
		fout = os.path.join("./weapons/", os.path.split(fin)[1][:-9])
		export_one_model(fin, fout)		
	for fin in glob.glob("../effect_rip/unpacked/AP_JUD*.unpacked"):
		fout = os.path.join("./weapons/", os.path.split(fin)[1][:-9])
		export_one_model(fin, fout)		
	for fin in glob.glob("../effect_rip/unpacked/W_SPE_J_*.unpacked"):
		fout = os.path.join("./weapons/", os.path.split(fin)[1][:-9])
		export_one_model(fin, fout)		
								
def export_one_model(fin, fout):
	fin = os.path.normpath(fin)
	fout = os.path.normpath(fout)
	os.system("mkdir tmp")
	os.system("python fps4_spliter.py -f %s -o ./tmp" % fin)
	os.system("python export_model.py -r ./tmp -o %s" % fout)
	os.system("del /Q tmp\\*.*")
	
if __name__ == '__main__':
	#export_yuri_weapons()
	#export_one_model("../effect_rip/unpacked/W_ARE_00_00.unpacked",
	#	"weapons/W_ARE_00_00",)
	#export_one_model("../effect_rip/unpacked/W_YGT_01_00.unpacked", "../effect_rip/models/W_YGT_01_00")
	export_judith_weapons()