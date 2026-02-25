import numpy as np
import bpy
from .. import analytics

# 0th-order spherical harmonic constant: used to recover RGB from f_dc coefficients
_SH_C0 = 0.28209479177387814

# Structured dtype for the .splat binary format (32 bytes per splat, little-endian)
_SPLAT_BIN_DTYPE = np.dtype([
    ('x', '<f4'), ('y', '<f4'), ('z', '<f4'),       # position
    ('sx', '<f4'), ('sy', '<f4'), ('sz', '<f4'),     # scale (linear, not log)
    ('r', 'u1'), ('g', 'u1'), ('b', 'u1'), ('a', 'u1'),       # RGBA
    ('q0', 'u1'), ('q1', 'u1'), ('q2', 'u1'), ('q3', 'u1'),   # rotation quaternion
])


def _count_f_rest(attributes) -> int:
    """Returns the number of f_rest_N scalar attributes present."""
    count = 0
    while f'f_rest_{count}' in attributes:
        count += 1
    return count


def _build_prop_names(f_rest_count: int) -> list[str]:
    """Returns the ordered list of PLY property names for a Gaussian Splat."""
    names = ['x', 'y', 'z', 'nx', 'ny', 'nz']
    names += [f'f_dc_{i}' for i in range(3)]
    names += [f'f_rest_{i}' for i in range(f_rest_count)]
    names += ['opacity', 'scale_0', 'scale_1', 'scale_2', 'rot_0', 'rot_1', 'rot_2', 'rot_3']
    return names


def _extract_columns(obj, f_rest_count: int, apply_transforms: bool) -> tuple[int, list]:
    """Extract numpy column arrays from a single splat object."""
    attrs = obj.data.attributes
    count = len(attrs['position'].data)

    def get_float(name, default=0.0):
        attr = attrs.get(name)
        if attr and attr.data_type == 'FLOAT':
            col = np.empty(count, dtype=np.float32)
            attr.data.foreach_get('value', col)
            return col
        return np.full(count, default, dtype=np.float32)

    # Position
    pos_arr = np.empty(count * 3, dtype=np.float32)
    attrs['position'].data.foreach_get('vector', pos_arr)
    pos = pos_arr.reshape(-1, 3)

    if apply_transforms:
        mw = np.array(obj.matrix_world)
        pos = pos @ mw[:3, :3].T + mw[:3, 3]

    columns = [pos[:, 0], pos[:, 1], pos[:, 2]]           # x, y, z
    columns += [np.zeros(count, dtype=np.float32)] * 3     # nx, ny, nz (unused in 3DGS)
    columns += [get_float(f'f_dc_{i}') for i in range(3)]
    columns += [get_float(f'f_rest_{i}') for i in range(f_rest_count)]
    columns.append(get_float('opacity', default=0.0))
    columns += [get_float(f'scale_{i}', default=0.0) for i in range(3)]
    columns += [get_float(f'rot_{i}', default=0.0) for i in range(4)]

    return count, columns


@analytics.track_event(
    "export_splat",
    lambda objects, filepath, use_ascii=False, apply_transforms=False: {
        "format": "ascii" if use_ascii else "binary",
        "object_count": len(objects),
    }
)
def export_splat_ply(objects, filepath, use_ascii=False, apply_transforms=False):
    """
    Export Gaussian Splat objects to a standard 3DGS PLY file.

    All scalar fields (f_dc, f_rest, opacity, scale, rot) are written as float32.
    apply_transforms only affects splat positions; scale/rotation splat properties
    are written as-is (they are already expressed in local object space by convention).
    """
    if not objects:
        return False, "No objects to export"

    ref_attrs = objects[0].data.attributes
    f_rest_count = _count_f_rest(ref_attrs)
    prop_names = _build_prop_names(f_rest_count)
    total_vertices = sum(len(obj.data.attributes['position'].data) for obj in objects)

    try:
        with open(filepath, 'wb' if not use_ascii else 'w') as f:
            # --- Header ---
            if use_ascii:
                f.write("ply\n")
                f.write("format ascii 1.0\n")
                f.write(f"element vertex {total_vertices}\n")
                for name in prop_names:
                    f.write(f"property float {name}\n")
                f.write("end_header\n")
            else:
                f.write(b"ply\n")
                f.write(b"format binary_little_endian 1.0\n")
                f.write(f"element vertex {total_vertices}\n".encode())
                for name in prop_names:
                    f.write(f"property float {name}\n".encode())
                f.write(b"end_header\n")

            # --- Data ---
            dtype_list = [(name, 'f4') for name in prop_names]

            for obj in objects:
                count, columns = _extract_columns(obj, f_rest_count, apply_transforms)
                if count == 0:
                    continue

                if use_ascii:
                    stacked = np.column_stack(columns)
                    np.savetxt(f, stacked, fmt='%.6f')
                else:
                    structured = np.zeros(count, dtype=dtype_list)
                    for name, col in zip(prop_names, columns):
                        structured[name] = col
                    f.write(structured.tobytes())

        return True, f"Exported {total_vertices} splats."

    except Exception as e:
        return False, str(e)


SplatFileHandler = None

if hasattr(bpy.types, "FileHandler"):
    class SplatFileHandler(bpy.types.FileHandler):
        bl_idname = "ply_splat_handler"
        bl_label = "Gaussian Splat (.ply)"
        bl_export_operator = "export_mesh.ply_splat_panel"
        bl_file_extensions = ".ply"


# ---------------------------------------------------------------------------
# .splat binary format (antimatter15 / compact, 32 bytes per splat)
# ---------------------------------------------------------------------------

def _extract_splat_bin_data(obj, apply_transforms: bool):
    """
    Extract and pack a single object into a structured numpy array
    matching _SPLAT_BIN_DTYPE (32 bytes per splat).

    Conversions applied:
      scale      : exp(log_scale)   — stored linear, not log
      color RGB  : clamp((0.5 + SH_C0 * f_dc) * 255, 0, 255)
      alpha      : clamp(sigmoid(opacity) * 255, 0, 255)
      rotation   : normalize quaternion, map [-1,1] → [0,255]
    """
    attrs = obj.data.attributes
    count = len(attrs['position'].data)

    def get_float(name, default=0.0):
        attr = attrs.get(name)
        if attr and attr.data_type == 'FLOAT':
            col = np.empty(count, dtype=np.float32)
            attr.data.foreach_get('value', col)
            return col
        return np.full(count, default, dtype=np.float32)

    # Position
    pos_arr = np.empty(count * 3, dtype=np.float32)
    attrs['position'].data.foreach_get('vector', pos_arr)
    pos = pos_arr.reshape(-1, 3)
    if apply_transforms:
        mw = np.array(obj.matrix_world)
        pos = pos @ mw[:3, :3].T + mw[:3, 3]

    # Scale: convert from log-space to linear
    log_scales = np.stack([get_float(f'scale_{i}', 0.0) for i in range(3)], axis=1)
    scales = np.exp(log_scales)  # (N, 3)

    # Color: bake 0th-order SH to RGB
    dc = np.stack([get_float(f'f_dc_{i}') for i in range(3)], axis=1)  # (N, 3)
    rgb = np.clip((0.5 + _SH_C0 * dc) * 255.0, 0, 255).astype(np.uint8)

    # Alpha: sigmoid activation on stored opacity logit
    opacity = get_float('opacity', 0.0)
    alpha = np.clip((1.0 / (1.0 + np.exp(-opacity))) * 255.0, 0, 255).astype(np.uint8)

    # Rotation: normalize quaternion, pack into [0, 255]
    rot = np.stack([get_float(f'rot_{i}', 0.0) for i in range(4)], axis=1)  # (N, 4)
    norms = np.linalg.norm(rot, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    rot_norm = rot / norms
    rot_u8 = np.clip((0.5 + rot_norm * 0.5) * 255.0, 0, 255).astype(np.uint8)

    structured = np.zeros(count, dtype=_SPLAT_BIN_DTYPE)
    structured['x'] = pos[:, 0]
    structured['y'] = pos[:, 1]
    structured['z'] = pos[:, 2]
    structured['sx'] = scales[:, 0]
    structured['sy'] = scales[:, 1]
    structured['sz'] = scales[:, 2]
    structured['r'] = rgb[:, 0]
    structured['g'] = rgb[:, 1]
    structured['b'] = rgb[:, 2]
    structured['a'] = alpha
    structured['q0'] = rot_u8[:, 0]
    structured['q1'] = rot_u8[:, 1]
    structured['q2'] = rot_u8[:, 2]
    structured['q3'] = rot_u8[:, 3]

    return count, structured


@analytics.track_event(
    "export_splat_bin",
    lambda objects, filepath, apply_transforms=False: {
        "object_count": len(objects),
    }
)
def export_splat_bin(objects, filepath, apply_transforms=False):
    """
    Export Gaussian Splat objects to the compact .splat binary format.

    The file has no header: it is a flat sequence of 32-byte records,
    one per splat. The number of splats is implicitly file_size / 32.
    Higher-order SH coefficients (f_rest) are discarded; color is baked
    from the 0th-order DC component only (no view-dependent effects).
    """
    if not objects:
        return False, "No objects to export"

    total_vertices = sum(len(obj.data.attributes['position'].data) for obj in objects)

    try:
        with open(filepath, 'wb') as f:
            for obj in objects:
                count, structured = _extract_splat_bin_data(obj, apply_transforms)
                if count == 0:
                    continue
                f.write(structured.tobytes())

        return True, f"Exported {total_vertices} splats."

    except Exception as e:
        return False, str(e)


SplatBinFileHandler = None

if hasattr(bpy.types, "FileHandler"):
    class SplatBinFileHandler(bpy.types.FileHandler):
        bl_idname = "splat_bin_handler"
        bl_label = "Gaussian Splat (.splat)"
        bl_export_operator = "export_mesh.splat_panel"
        bl_file_extensions = ".splat"
