# Minimum set of attributes that identifies a Gaussian Splat (vs a plain point cloud)
_SPLAT_REQUIRED_ATTRS = frozenset({'scale_0', 'rot_0', 'opacity', 'f_dc_0'})


def get_non_pointcloud_names(objects):
    """Returns names of objects whose base type is not POINTCLOUD."""
    return [obj.name for obj in objects if obj.type != 'POINTCLOUD']


def is_gaussian_splat(obj) -> bool:
    """Returns True if the object is a PointCloud with Gaussian Splat attributes."""
    if obj.type != 'POINTCLOUD':
        return False
    attr_names = {a.name for a in obj.data.attributes}
    return _SPLAT_REQUIRED_ATTRS.issubset(attr_names)


def get_non_splat_names(objects) -> list:
    """Returns names of objects that are not Gaussian Splats."""
    return [obj.name for obj in objects if not is_gaussian_splat(obj)]
