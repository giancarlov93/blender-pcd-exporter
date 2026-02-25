from bpy.props import BoolProperty
from .. import utils


class ExportPLYBase:
    """Shared properties for PLY exporters."""

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

    @staticmethod
    def get_non_pointcloud_names(objects):
        return utils.get_non_pointcloud_names(objects)

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


class ExportSplatBinBase:
    """Shared properties for .splat binary format exporters."""

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to the exported objects (e.g. Geometry Nodes)",
        default=True,
    )

    apply_transforms: BoolProperty(
        name="Apply Transformations",
        description="Apply object location/rotation/scale to splat positions. "
                    "Splat-specific properties (scale, rotation) are written as-is.",
        default=True,
    )

    @staticmethod
    def get_non_splat_names(objects):
        return utils.get_non_splat_names(objects)

    def get_objects(self, context, objects, apply_modifiers):
        depsgraph = context.evaluated_depsgraph_get() if apply_modifiers else None

        objects_to_export = []
        for obj in objects:
            final_obj = obj
            if apply_modifiers:
                final_obj = obj.evaluated_get(depsgraph)

            if utils.is_gaussian_splat(final_obj):
                objects_to_export.append(final_obj)

        return objects_to_export


class ExportSplatBase:
    """Shared properties for Gaussian Splat exporters."""

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
        description="Apply object location/rotation/scale to splat positions. "
                    "Splat-specific properties (scale, rotation) are written as-is.",
        default=True,
    )

    @staticmethod
    def get_non_splat_names(objects):
        return utils.get_non_splat_names(objects)

    def get_objects(self, context, objects, apply_modifiers):
        depsgraph = context.evaluated_depsgraph_get() if apply_modifiers else None

        objects_to_export = []
        for obj in objects:
            final_obj = obj
            if apply_modifiers:
                final_obj = obj.evaluated_get(depsgraph)

            if utils.is_gaussian_splat(final_obj):
                objects_to_export.append(final_obj)

        return objects_to_export
