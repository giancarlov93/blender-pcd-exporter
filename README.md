# Point Cloud Exporter (.ply)

A lightweight and efficient dedicated exporter for Blender's **Point Cloud** data structures.

Ideally suited for workflows involving **Geometry Nodes**, this extension allows you to export your generated points directly to the industry-standard **PLY** (Polygon File Format).

## ✨ Key Features

- **Native Support**: Designed specifically for Blender's `PointCloud` object type.
- **Geometry Nodes Ready**: Automatically **applies modifiers** before export, ensuring that your procedurally generated points are captured correctly (can be disabled).
- **Format Options**: Supports both **ASCII** (readable) and **Binary** (compact/fast) PLY formats.
- **Seamless Integration**:
  - Accessible via `File > Export > Point Cloud (.ply)`.
  - Fully integrated into Blender 4.2+ **Exporters Panel**.

## 🚀 Usage

### via Blender UI

1. Select one or more Point Cloud objects in the 3D Viewport.
2. Navigate to **File > Export > Point Cloud (.ply)**.
3. In the export dialog, choose your preferences:
   - **Selection Only**: Export only specific objects.
   - **Apply Modifiers**: (Recommended) Evaluate Geometry Nodes before exporting.
   - **Format**: Binary (default) or ASCII.
4. Click **Export**.

### via Blender 4.2+ Exporters Panel

1. Make a new collection and link your Point Cloud objects to it.
2. Navigate to **Collection tab > Exporters**.
3. Add a new exporter and select **Point Cloud (.ply)**.
4. In the export dialog, choose your preferences:
   - **Format**: Binary (default) or ASCII.
   - **Apply Modifiers**: (Recommended) Evaluate Geometry Nodes before exporting.
5. Click **Export**.

## compatibility

- **Blender 4.2** or newer is required.
