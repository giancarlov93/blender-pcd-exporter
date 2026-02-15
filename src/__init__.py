import bpy
import sys
from . import exporter

bl_info = {
    "name": "@GV - PointCloud & Splat Exporter (.ply)",
    "author": "Giancarlo Viali",
    "version": (0, 0, 2),
    "blender": (4, 0, 0),
    "location": "File > Export > Point Cloud (.ply)",
    "description": "Export PointCloud and Splat data to PLY format",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

if hasattr(bpy.types, "FileHandler"):
    class PLYFileHandler(bpy.types.FileHandler):
        bl_idname = "ply_pcd_handler"
        bl_label = "Point Cloud (.ply)"
        bl_export_operator = "export_mesh.ply_pcd_panel"
        bl_file_extensions = ".ply"

def menu_func_export(self, context):
    self.layout.operator(exporter.ExportPLYMenu.bl_idname, text="Point Cloud (.ply)")

def register():
    bpy.utils.register_class(exporter.ExportPLYMenu)
    bpy.utils.register_class(exporter.ExportPLYPanel)
    if hasattr(bpy.types, "FileHandler"):
        bpy.utils.register_class(PLYFileHandler)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    if hasattr(bpy.types, "FileHandler"):
        bpy.utils.unregister_class(PLYFileHandler)
    bpy.utils.unregister_class(exporter.ExportPLYPanel)
    bpy.utils.unregister_class(exporter.ExportPLYMenu)