import numpy as np
from .. import analytics

# Attributes handled with special PLY naming / transform logic
_SPECIAL_ATTRS = frozenset({'position', 'normal'})


def _build_ply_properties(attributes):
    """
    Build the ply_properties list from a Blender point cloud's attribute collection.

    Returns (props, error_message).  Each entry in props is a 5-tuple:
        (ply_name, ply_type, components, blender_attr_name, sub_index)

    Attribute mapping rules:
      position       → x, y, z           (float, handled with transform)
      normal         → nx, ny, nz         (float, handled with transform)
      color / Color  → red, green, blue   (uchar, canonical PLY color names)
      FLOAT          → <name>             (float)
      INT / INT8     → <name>             (int)
      BOOLEAN        → <name>             (uchar 0/1)
      FLOAT_VECTOR   → <name>_x/y/z      (float × 3)
      FLOAT2         → <name>_u/v        (float × 2)
      FLOAT_COLOR    → <name>_r/g/b/a    (float × 4)
      BYTE_COLOR     → <name>_r/g/b/a    (uchar × 4)
      QUATERNION     → <name>_w/x/y/z    (float × 4)
    """
    props = []
    handled = set()

    # --- Position (mandatory) ---
    if 'position' not in attributes:
        return None, "Point Cloud has no 'position' attribute."
    props += [
        ('x', 'float', 3, 'position', 0),
        ('y', 'float', 3, 'position', 1),
        ('z', 'float', 3, 'position', 2),
    ]
    handled.add('position')

    # --- Normal (optional, canonical PLY names) ---
    if 'normal' in attributes:
        props += [
            ('nx', 'float', 3, 'normal', 0),
            ('ny', 'float', 3, 'normal', 1),
            ('nz', 'float', 3, 'normal', 2),
        ]
        handled.add('normal')

    # --- Color (optional, canonical PLY names red/green/blue) ---
    color_attr = attributes.get('color') or attributes.get('Color')
    if color_attr:
        props += [
            ('red',   'uchar', 4, color_attr.name, 0),
            ('green', 'uchar', 4, color_attr.name, 1),
            ('blue',  'uchar', 4, color_attr.name, 2),
        ]
        handled.add(color_attr.name)

    # --- All remaining POINT-domain attributes ---
    for attr in attributes:
        if attr.name in handled or attr.domain != 'POINT':
            continue
        name = attr.name
        dt = attr.data_type

        if dt == 'FLOAT':
            props.append((name, 'float', 1, name, 0))
        elif dt in ('INT', 'INT8'):
            props.append((name, 'int', 1, name, 0))
        elif dt == 'BOOLEAN':
            props.append((name, 'uchar', 1, name, 0))
        elif dt == 'FLOAT_VECTOR':
            for i, s in enumerate(('_x', '_y', '_z')):
                props.append((name + s, 'float', 3, name, i))
        elif dt == 'FLOAT2':
            for i, s in enumerate(('_u', '_v')):
                props.append((name + s, 'float', 2, name, i))
        elif dt == 'FLOAT_COLOR':
            for i, s in enumerate(('_r', '_g', '_b', '_a')):
                props.append((name + s, 'float', 4, name, i))
        elif dt == 'BYTE_COLOR':
            for i, s in enumerate(('_r', '_g', '_b', '_a')):
                props.append((name + s, 'uchar', 4, name, i))
        elif dt == 'QUATERNION':
            for i, s in enumerate(('_w', '_x', '_y', '_z')):
                props.append((name + s, 'float', 4, name, i))
        # STRING and unknown types: skip silently

    return props, None


def _read_column(attr, count, sub_index, ply_type):
    """Read a single PLY component from a Blender attribute as a numpy 1-D array."""
    dt = attr.data_type

    if dt == 'FLOAT':
        col = np.empty(count, dtype=np.float32)
        attr.data.foreach_get('value', col)
        return col

    elif dt in ('INT', 'INT8'):
        col = np.empty(count, dtype=np.int32)
        attr.data.foreach_get('value', col)
        return col

    elif dt == 'BOOLEAN':
        col = np.empty(count, dtype=np.bool_)
        attr.data.foreach_get('value', col)
        return col.astype(np.uint8)

    elif dt == 'FLOAT_VECTOR':
        arr = np.empty(count * 3, dtype=np.float32)
        attr.data.foreach_get('vector', arr)
        return arr[sub_index::3]

    elif dt == 'FLOAT2':
        arr = np.empty(count * 2, dtype=np.float32)
        attr.data.foreach_get('vector', arr)
        return arr[sub_index::2]

    elif dt in ('FLOAT_COLOR', 'BYTE_COLOR'):
        arr = np.empty(count * 4, dtype=np.float32)
        attr.data.foreach_get('color', arr)
        col = arr[sub_index::4]
        if ply_type == 'uchar':
            return (col * 255.0).astype(np.uint8)
        return col

    elif dt == 'QUATERNION':
        arr = np.empty(count * 4, dtype=np.float32)
        attr.data.foreach_get('value', arr)
        return arr[sub_index::4]

    else:
        return np.zeros(count, dtype=np.float32)


def _get_fmt_string(properties):
    fmts = []
    for _, prop_type, _, _, _ in properties:
        if prop_type == 'float':
            fmts.append('%.6f')
        elif prop_type in ('uchar', 'int'):
            fmts.append('%d')
        else:
            fmts.append('%s')
    return ' '.join(fmts)


def _ply_type_to_numpy(ply_type):
    return {'float': 'f4', 'uchar': 'u1', 'int': 'i4'}.get(ply_type, 'f4')


@analytics.track_event(
    "export_ply",
    lambda objects, filepath, use_ascii=False, apply_transforms=False: {
        "format": "ascii" if use_ascii else "binary",
        "object_count": len(objects),
    }
)
def export_ply(objects, filepath, use_ascii=False, apply_transforms=False):
    """
    Export a list of evaluated PointCloud objects to a PLY file.
    All POINT-domain attributes are preserved; unrecognised types are skipped.
    """
    if not objects:
        return False, "No objects to export"

    ply_properties, error = _build_ply_properties(objects[0].data.attributes)
    if error:
        return False, error

    total_vertices = sum(len(obj.data.attributes['position'].data) for obj in objects)

    try:
        with open(filepath, 'wb' if not use_ascii else 'w') as f:
            # --- Header ---
            def w(line):
                f.write(line.encode() if not use_ascii else line)

            w("ply\n")
            w(f"format {'ascii' if use_ascii else 'binary_little_endian'} 1.0\n")
            w(f"element vertex {total_vertices}\n")
            for prop_name, prop_type, _, _, _ in ply_properties:
                w(f"property {prop_type} {prop_name}\n")
            w("end_header\n")

            # --- Data ---
            dtype_list = [
                (prop_name, _ply_type_to_numpy(prop_type))
                for prop_name, prop_type, _, _, _ in ply_properties
            ]

            for obj in objects:
                count = len(obj.data.attributes['position'].data)
                if count == 0:
                    continue

                attrs = obj.data.attributes
                transformed_cache = {}

                if apply_transforms:
                    mw = np.array(obj.matrix_world)
                    R, T = mw[:3, :3], mw[:3, 3]

                    pos_attr = attrs.get('position')
                    if pos_attr:
                        arr = np.empty(count * 3, dtype=np.float32)
                        pos_attr.data.foreach_get('vector', arr)
                        transformed_cache['position'] = arr.reshape(-1, 3) @ R.T + T

                    norm_attr = attrs.get('normal')
                    if norm_attr:
                        arr = np.empty(count * 3, dtype=np.float32)
                        norm_attr.data.foreach_get('vector', arr)
                        mat_norm = np.array(
                            obj.matrix_world.to_3x3().inverted_safe().transposed()
                        )
                        n = arr.reshape(-1, 3) @ mat_norm.T
                        norms = np.linalg.norm(n, axis=1, keepdims=True)
                        norms[norms == 0] = 1.0
                        transformed_cache['normal'] = n / norms

                data_columns = []
                for prop_name, prop_type, _, attr_name, sub_index in ply_properties:
                    if attr_name in transformed_cache:
                        data_columns.append(transformed_cache[attr_name][:, sub_index])
                    else:
                        attr = attrs.get(attr_name)
                        if attr is None:
                            data_columns.append(np.zeros(count, dtype=np.float32))
                        else:
                            data_columns.append(
                                _read_column(attr, count, sub_index, prop_type)
                            )

                if use_ascii:
                    np.savetxt(f, np.column_stack(data_columns),
                               fmt=_get_fmt_string(ply_properties))
                else:
                    structured = np.zeros(count, dtype=dtype_list)
                    for (prop_name, _, _, _, _), col in zip(ply_properties, data_columns):
                        structured[prop_name] = col
                    f.write(structured.tobytes())

        return True, f"Exported {total_vertices} points."

    except Exception as e:
        return False, str(e)


import bpy

PLYFileHandler = None

if hasattr(bpy.types, "FileHandler"):
    class PLYFileHandler(bpy.types.FileHandler):
        bl_idname = "ply_pcd_handler"
        bl_label = "Point Cloud (.ply)"
        bl_export_operator = "export_mesh.ply_pcd_panel"
        bl_file_extensions = ".ply"
