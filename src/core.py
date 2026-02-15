import struct
import numpy as np

def _get_fmt_string(properties):
    fmts = []
    for _, prop_type, _, _, _ in properties:
        if prop_type == 'float':
            fmts.append('%.6f')
        elif prop_type == 'uchar':
            fmts.append('%d')
        else:
            fmts.append('%s')
    return ' '.join(fmts)

def export_ply(objects, filepath, use_ascii=False, apply_transforms=False):
    """
    Export a list of objects (assumed to be evaluated PointClouds) to a PLY file.
    """
    if not objects:
        return False, "No objects to export"

    reference_obj = objects[0]
    attributes = reference_obj.data.attributes
    
    ply_properties = [] # List of (name, type, count, blender_attr_name, sub_index)
    
    # POSITION is mandatory
    if 'position' in attributes:
        ply_properties.append(('x', 'float', 1, 'position', 0))
        ply_properties.append(('y', 'float', 1, 'position', 1))
        ply_properties.append(('z', 'float', 1, 'position', 2))
    else:
        return False, "Point Cloud has no 'position' attribute."

    # Normals
    if 'normal' in attributes:
            ply_properties.append(('nx', 'float', 1, 'normal', 0))
            ply_properties.append(('ny', 'float', 1, 'normal', 1))
            ply_properties.append(('nz', 'float', 1, 'normal', 2))
    
    # Colors
    color_attr = attributes.get('color') or attributes.get('Color')
    if color_attr:
        ply_properties.append(('red', 'uchar', 1, color_attr.name, 0))
        ply_properties.append(('green', 'uchar', 1, color_attr.name, 1))
        ply_properties.append(('blue', 'uchar', 1, color_attr.name, 2))

    # Count Total Vertices
    total_vertices = sum(len(obj.data.attributes['position'].data) for obj in objects)
    
    try:
        with open(filepath, 'wb' if not use_ascii else 'w') as f:
            # HEADER
            header = []
            header.append(b"ply\n" if not use_ascii else "ply\n")
            fmt = "ascii" if use_ascii else "binary_little_endian"
            header.append(f"format {fmt} 1.0\n".encode('utf-8') if not use_ascii else f"format {fmt} 1.0\n")
            header.append(f"element vertex {total_vertices}\n".encode('utf-8') if not use_ascii else f"element vertex {total_vertices}\n")
            
            for prop_name, prop_type, _, _, _ in ply_properties:
                header.append(f"property {prop_type} {prop_name}\n".encode('utf-8') if not use_ascii else f"property {prop_type} {prop_name}\n")
            
            header.append(b"end_header\n" if not use_ascii else "end_header\n")
            
            for line in header:
                f.write(line)

            # DATA
            for obj in objects:
                count = len(obj.data.attributes['position'].data)
                if count == 0: continue
                
                # Cache for transformed attributes
                # Maps attr_name -> numpy array (N, 3)
                transformed_cache = {}

                if apply_transforms:
                    # Capture Matrix World
                    # obj.matrix_world is a mathutils.Matrix
                    # convert to numpy 4x4
                    mw = np.array(obj.matrix_world)
                    R = mw[:3, :3] # Rotation + Scale
                    T = mw[:3, 3]  # Translation

                    # Transform Position
                    pos_attr = obj.data.attributes.get('position')
                    if pos_attr:
                        arr = np.empty(count * 3, dtype=np.float32)
                        pos_attr.data.foreach_get('vector', arr)
                        pos_vec = arr.reshape(-1, 3)
                        
                        # Apply: v_world = v_local @ R.T + T
                        pos_world = pos_vec @ R.T + T
                        transformed_cache['position'] = pos_world

                    # Transform Normal
                    norm_attr = obj.data.attributes.get('normal')
                    if norm_attr:
                        arr = np.empty(count * 3, dtype=np.float32)
                        norm_attr.data.foreach_get('vector', arr)
                        norm_vec = arr.reshape(-1, 3)
                        
                        # Normal Matrix: (M^-1).T (upper 3x3)
                        # We use mathutils to compute inverted-safe then transpose
                        mat_norm = np.array(obj.matrix_world.to_3x3().inverted_safe().transposed())
                        
                        # Apply: n_world = n_local @ mat_norm.T 
                        # (because standard mul is RowVector @ Matrix)
                        norm_world = norm_vec @ mat_norm.T
                        
                        # Normalize
                        norms = np.linalg.norm(norm_world, axis=1, keepdims=True)
                        norms[norms == 0] = 1.0
                        norm_world /= norms
                        
                        transformed_cache['normal'] = norm_world

                
                data_columns = []
                
                for prop_name, prop_type, _, attr_name, sub_index in ply_properties:
                    
                    # Check if we have a transformed version cached
                    if attr_name in transformed_cache:
                        col = transformed_cache[attr_name][:, sub_index]
                    else:
                        attr = obj.data.attributes.get(attr_name)
                        if attr is None:
                            col = np.zeros(count, dtype=np.float32)
                        else:
                            arr_len = count * (3 if attr.data_type.endswith('VECTOR') else 1)
                            
                            if attr.data_type == 'FLOAT_VECTOR':
                                arr = np.empty(count * 3, dtype=np.float32)
                                attr.data.foreach_get('vector', arr)
                                col = arr[sub_index::3]
                            
                            elif attr.data_type == 'FLOAT_COLOR':
                                arr = np.empty(count * 4, dtype=np.float32)
                                attr.data.foreach_get('color', arr)
                                col = arr[sub_index::4]
                                if prop_type == 'uchar':
                                    col = (col * 255).astype(np.uint8)
                                    
                            elif attr.data_type == 'BYTE_COLOR':
                                arr = np.empty(count * 4, dtype=np.float32)
                                attr.data.foreach_get('color', arr)
                                col = arr[sub_index::4]
                                if prop_type == 'uchar':
                                    col = (col * 255).astype(np.uint8)
                                    
                            elif attr.data_type == 'FLOAT':
                                col = np.empty(count, dtype=np.float32)
                                attr.data.foreach_get('value', col)
                            else:
                                col = np.zeros(count, dtype=np.float32)

                    data_columns.append(col)
                
                stacked = np.column_stack(data_columns)
                
                if use_ascii:
                    np.savetxt(f, stacked, fmt=_get_fmt_string(ply_properties))
                else:
                    dtype_list = []
                    for prop_name, prop_type, _, _, _ in ply_properties:
                        numpy_type = 'f4' if prop_type == 'float' else 'u1'
                        dtype_list.append((prop_name, numpy_type))
                    
                    structured_arr = np.zeros(count, dtype=dtype_list)
                    for i, (prop_name, _, _, _, _) in enumerate(ply_properties):
                        structured_arr[prop_name] = data_columns[i]
                        
                    f.write(structured_arr.tobytes())
                    
        return True, f"Exported {total_vertices} points."
        
    except Exception as e:
        return False, str(e)
