from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from . import core

class ExportPLYBase:
    """Shared properties for PLY Exporters"""
    use_ascii: BoolProperty(
        name="ASCII",
        description="Export as ASCII PLY (useful for debugging, but larger files)",
        default=False,
    )

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to the exported objects (e.g. Geometry Nodes)",
        default=True,
    )

    apply_transforms: BoolProperty(
        name="Apply Transformations",
        description="Apply object transformations (Location, Rotation, Scale) to the exported data",
        default=True,
    )

    def get_objects(self, context, objects, apply_modifiers):
        depsgraph = context.evaluated_depsgraph_get() if apply_modifiers else None
        
        objects_to_export = []
        for obj in objects:
            final_obj = obj
            if apply_modifiers:
                final_obj = obj.evaluated_get(depsgraph)
            
            if final_obj.type == 'POINTCLOUD':
                objects_to_export.append(final_obj)
        
        return objects_to_export

class ExportPLYMenu(Operator, ExportHelper, ExportPLYBase):
    """Export Point Cloud Data to PLY (Menu)"""
    bl_idname = "export_mesh.ply_pcd"
    bl_label = "Point Cloud (.ply)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".ply"
    filter_glob: StringProperty(
        default="*.ply",
        options={'HIDDEN'},
    )

    selection_only: BoolProperty(
        name="Selection Only",
        description="Export only selected objects",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_ascii")
        layout.prop(self, "apply_modifiers")
        layout.prop(self, "apply_transforms")
        layout.prop(self, "selection_only")

    def execute(self, context):
        if self.selection_only:
            source_objects = context.selected_objects
        else:
            source_objects = context.scene.objects
            
        objects = self.get_objects(context, source_objects, self.apply_modifiers)
        
        success, message = core.export_ply(objects, self.filepath, self.use_ascii, self.apply_transforms)
        
        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

class ExportPLYPanel(Operator, ExportPLYBase):
    """Export Point Cloud Data to PLY (Panel)"""
    bl_idname = "export_mesh.ply_pcd_panel"
    bl_label = "Point Cloud (.ply)"
    bl_options = {'PRESET', 'UNDO'}

    filepath: StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
        options={'HIDDEN', 'SKIP_SAVE'}, 
    )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_ascii")
        layout.prop(self, "apply_modifiers")
        layout.prop(self, "apply_transforms")

    def execute(self, context):        
        candidates = []
        
        if hasattr(context, "collection") and context.collection:
            candidates = list(context.collection.all_objects)
            
        if not candidates:
            candidates = list(context.selected_objects)
            
        if not candidates:
            self.report({'WARNING'}, "No objects found to export (checked Collection and Selection).")
            return {'CANCELLED'}

        objects = self.get_objects(context, candidates, self.apply_modifiers)
        
        if not objects:
            self.report({'WARNING'}, "No Point Cloud objects found in the target collection/selection.")
            return {'CANCELLED'}
        
        success, message = core.export_ply(objects, self.filepath, self.use_ascii, self.apply_transforms)
        
        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}
