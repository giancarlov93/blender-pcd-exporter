import bpy
from . import analytics, formats, ui, operators

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

_MENU_FUNCS = [
    ui.menu_func_export,
    ui.menu_func_export_splat,
    ui.menu_func_export_splat_bin,
]


def register():
    for cls in ui.classes + operators.classes + formats.classes:
        bpy.utils.register_class(cls)
    for fn in _MENU_FUNCS:
        bpy.types.TOPBAR_MT_file_export.append(fn)
    analytics.track("addon_register")


def unregister():
    analytics.track("addon_unregister")
    for fn in reversed(_MENU_FUNCS):
        bpy.types.TOPBAR_MT_file_export.remove(fn)
    for cls in reversed(formats.classes + operators.classes + ui.classes):
        bpy.utils.unregister_class(cls)
