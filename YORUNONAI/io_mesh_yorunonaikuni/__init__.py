bl_info = {
	"name": "Yoru No Nai Kuni G1M Format",
	"author": "Qing Guo",
	"blender": (2, 72, 0),
	"location": "File > Import-Export",
	"description": "Import Yoru No Nai Kuni mesh and skeleton data.",
	"warning": "",
	"category": "Import-Export"}

# To support reload properly, try to access a package var,
# if it's there, reload everything
if "bpy" in locals():
	import importlib
	if "g1m_importer" in locals():
		importlib.reload(g1m_importer)
		
from . import g1m_importer

import os
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (CollectionProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty)
		
class ImportG1M(bpy.types.Operator, ImportHelper):
	"""Load a Yoru No Nai Kuni g1m file."""
	bl_idname = "import_mesh.g1m"
	bl_label = "Import Yoru No Nai Kuni G1M"
	bl_options = {'UNDO'}

	files = CollectionProperty(name="File Path",
						  description="File path used for importing the Yoru No Nai Kuni g1m file",
						  type=bpy.types.OperatorFileListElement)

	directory = StringProperty()

	filename_ext = ".g1m"
	filter_glob = StringProperty(default="*.g1m", options={'HIDDEN'})

	def execute(self, context):
		paths = [os.path.join(self.directory, name.name)
				 for name in self.files]
		if not paths:
			paths.append(self.filepath)

		for path in paths:
			g1m_imporeter.import_g1m(path)

		return {'FINISHED'}

def menu_func_import(self, context):
	self.layout.operator(ImportG1M.bl_idname, text="Yoru No Nai Kuni Mesh (.g1m)")
		
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == '__main__':
	register()