from .preferences import AddonPreferences
from .analytics_prompt import AnalyticsPromptAction

classes = [AddonPreferences, AnalyticsPromptAction]


def menu_func_export(self, context):
    from ..operators.export import ExportPLYMenu
    self.layout.operator(ExportPLYMenu.bl_idname, text="Point Cloud (.ply)")


def menu_func_export_splat(self, context):
    from ..operators.export import ExportSplatMenu
    self.layout.operator(ExportSplatMenu.bl_idname, text="Gaussian Splat (.ply)")


def menu_func_export_splat_bin(self, context):
    from ..operators.export import ExportSplatBinMenu
    self.layout.operator(ExportSplatBinMenu.bl_idname, text="Gaussian Splat (.splat)")
