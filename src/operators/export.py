from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base import ExportPLYBase, ExportSplatBase, ExportSplatBinBase
from ..formats import export_ply, export_splat_ply, export_splat_bin
from ..ui.analytics_prompt import maybe_show_analytics_prompt


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

        source = context.selected_objects if self.selection_only else list(context.scene.objects)
        skipped = self.get_non_pointcloud_names(source)
        if skipped:
            box = layout.box()
            box.label(text=f"{len(skipped)} non-PointCloud object(s) will be skipped:", icon='ERROR')
            for name in skipped:
                box.label(text=f"  \u2022 {name}", icon='BLANK1')

    def execute(self, context):
        source_objects = context.selected_objects if self.selection_only else context.scene.objects
        objects = self.get_objects(context, source_objects, self.apply_modifiers)

        success, message = export_ply(objects, self.filepath, self.use_ascii, self.apply_transforms)

        if success:
            self.report({'INFO'}, message)
            maybe_show_analytics_prompt()
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

        candidates = []
        if hasattr(context, "collection") and context.collection:
            candidates = list(context.collection.all_objects)
        if not candidates:
            candidates = list(context.selected_objects)

        skipped = self.get_non_pointcloud_names(candidates)
        if skipped:
            box = layout.box()
            box.label(text=f"{len(skipped)} non-PointCloud object(s) will be skipped:", icon='ERROR')
            for name in skipped:
                box.label(text=f"  \u2022 {name}", icon='BLANK1')

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

        success, message = export_ply(objects, self.filepath, self.use_ascii, self.apply_transforms)

        if success:
            self.report({'INFO'}, message)
            maybe_show_analytics_prompt()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class ExportSplatMenu(Operator, ExportHelper, ExportSplatBase):
    """Export Gaussian Splat Data to PLY (Menu)"""
    bl_idname = "export_mesh.ply_splat"
    bl_label = "Gaussian Splat (.ply)"
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

        source = context.selected_objects if self.selection_only else list(context.scene.objects)
        skipped = self.get_non_splat_names(source)
        if skipped:
            box = layout.box()
            box.label(text=f"{len(skipped)} non-Splat object(s) will be skipped:", icon='ERROR')
            for name in skipped:
                box.label(text=f"  \u2022 {name}", icon='BLANK1')

    def execute(self, context):
        source_objects = context.selected_objects if self.selection_only else context.scene.objects
        objects = self.get_objects(context, source_objects, self.apply_modifiers)

        success, message = export_splat_ply(objects, self.filepath, self.use_ascii, self.apply_transforms)

        if success:
            self.report({'INFO'}, message)
            maybe_show_analytics_prompt()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class ExportSplatPanel(Operator, ExportSplatBase):
    """Export Gaussian Splat Data to PLY (Panel)"""
    bl_idname = "export_mesh.ply_splat_panel"
    bl_label = "Gaussian Splat (.ply)"
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

        candidates = []
        if hasattr(context, "collection") and context.collection:
            candidates = list(context.collection.all_objects)
        if not candidates:
            candidates = list(context.selected_objects)

        skipped = self.get_non_splat_names(candidates)
        if skipped:
            box = layout.box()
            box.label(text=f"{len(skipped)} non-Splat object(s) will be skipped:", icon='ERROR')
            for name in skipped:
                box.label(text=f"  \u2022 {name}", icon='BLANK1')

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
            self.report({'WARNING'}, "No Gaussian Splat objects found in the target collection/selection.")
            return {'CANCELLED'}

        success, message = export_splat_ply(objects, self.filepath, self.use_ascii, self.apply_transforms)

        if success:
            self.report({'INFO'}, message)
            maybe_show_analytics_prompt()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class ExportSplatBinMenu(Operator, ExportHelper, ExportSplatBinBase):
    """Export Gaussian Splat to compact .splat binary format (Menu)"""
    bl_idname = "export_mesh.splat"
    bl_label = "Gaussian Splat (.splat)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".splat"
    filter_glob: StringProperty(
        default="*.splat",
        options={'HIDDEN'},
    )

    selection_only: BoolProperty(
        name="Selection Only",
        description="Export only selected objects",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "apply_modifiers")
        layout.prop(self, "apply_transforms")
        layout.prop(self, "selection_only")

        source = context.selected_objects if self.selection_only else list(context.scene.objects)
        skipped = self.get_non_splat_names(source)
        if skipped:
            box = layout.box()
            box.label(text=f"{len(skipped)} non-Splat object(s) will be skipped:", icon='ERROR')
            for name in skipped:
                box.label(text=f"  \u2022 {name}", icon='BLANK1')

    def execute(self, context):
        source_objects = context.selected_objects if self.selection_only else context.scene.objects
        objects = self.get_objects(context, source_objects, self.apply_modifiers)

        success, message = export_splat_bin(objects, self.filepath, self.apply_transforms)

        if success:
            self.report({'INFO'}, message)
            maybe_show_analytics_prompt()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class ExportSplatBinPanel(Operator, ExportSplatBinBase):
    """Export Gaussian Splat to compact .splat binary format (Panel)"""
    bl_idname = "export_mesh.splat_panel"
    bl_label = "Gaussian Splat (.splat)"
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
        layout.prop(self, "apply_modifiers")
        layout.prop(self, "apply_transforms")

        candidates = []
        if hasattr(context, "collection") and context.collection:
            candidates = list(context.collection.all_objects)
        if not candidates:
            candidates = list(context.selected_objects)

        skipped = self.get_non_splat_names(candidates)
        if skipped:
            box = layout.box()
            box.label(text=f"{len(skipped)} non-Splat object(s) will be skipped:", icon='ERROR')
            for name in skipped:
                box.label(text=f"  \u2022 {name}", icon='BLANK1')

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
            self.report({'WARNING'}, "No Gaussian Splat objects found in the target collection/selection.")
            return {'CANCELLED'}

        success, message = export_splat_bin(objects, self.filepath, self.apply_transforms)

        if success:
            self.report({'INFO'}, message)
            maybe_show_analytics_prompt()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}
