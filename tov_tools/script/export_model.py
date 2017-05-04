import os
import sys
import glob
import argparse

def export_model(name_base):
	os.system(r"python .\script\mesh_parser.py %s.SPM" % name_base)
	os.system(r"python .\script\tex_decoder.py %s.TXM" % name_base)
	
def clean_up(dest):
	os.system("python .\script\obj_joiner.py")
	if not os.path.exists(dest):
		os.mkdir(dest)
	files = glob.glob("*.png")
	files.append("all.obj")
	files.append("all.mtl")
	
	for file_path in files:
		os.system("copy %s %s" % (file_path, dest))
	
	os.system("del *.obj")
	os.system("del *.mtl")
	os.system("del *.png")
	os.system("del *.bin")
	os.system("del *.dds")
	
def process_folder(root, dest):
	if root.endswith(".SPM"):
		name_base = os.path.splitext(root)[0]
		export_model(name_base)
	else:
		for dirpath, dirnames, filenames in os.walk(root):
			for filename in filenames:
				if filename.endswith(".SPM"):
					name_base = os.path.splitext(os.path.join(dirpath, filename))[0]
					export_model(name_base)
	clean_up(dest)

if __name__ == "__main__":
	
	description = "Automatically export model parts and join them together and clean up textures."
	
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument("-r", action="store", dest="root", default=".", type=str, help="Input folder, contains model parts.")
	parser.add_argument("-o", action="store", default=r".\tmp", dest="out_folder", type=str, help="Output folder, where the splitted files will go to.")
	
	args = parser.parse_args()
	
	process_folder(args.root, args.out_folder)