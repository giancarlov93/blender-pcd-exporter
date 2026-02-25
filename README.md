# PointCloud & Splat Exporter

Export Blender's native **Point Cloud** objects to the most common interchange formats for point cloud and Gaussian Splatting workflows — directly from `File > Export` or the Blender 4.2+ Exporters Panel.

---

## 📦 Export formats

### Point Cloud — PLY (`.ply`)

Exports all point attributes present in the object to a standard PLY file. Position, normals and colour use canonical property names for maximum compatibility with third-party software. Every additional scalar field, custom vector or boolean mask is preserved automatically — nothing is dropped.

### Gaussian Splat — PLY (`.ply`)

Exports in the standard **3D Gaussian Splatting** PLY layout used by training pipelines and most desktop viewers. All spherical harmonic coefficients are preserved, including the higher-order bands that encode view-dependent colour.

### Gaussian Splat — compact binary (`.splat`)

Exports in the compact **32-byte-per-splat** binary format compatible with antimatter15, Polycam, Luma AI and web-based viewers built on Three.js. Colour is baked from the base SH component; higher-order coefficients are discarded. The result is a small, headerless file that loads instantly in the browser.

---

## ✨ Key features

**Geometry Nodes compatible** — modifiers are evaluated before export by default, so procedurally generated point clouds are captured at their final computed state.

**World-space transforms** — optionally bakes the object's Location, Rotation and Scale into the exported coordinates, with correct handling for both positions and normals.

**Automatic splat detection** — the exporter recognises Gaussian Splat objects automatically. Non-matching objects are listed in the export dialog and skipped, so mixed selections are never a problem.

**ASCII and binary** — PLY exports support both formats. Binary is the default; ASCII is useful for inspection and debugging.

**Exporters Panel** — fully integrated into the Blender 4.2+ Exporters Panel. Attach an exporter to a collection and re-export with a single click, without opening a file dialog each time.

---

## 🚀 Usage

### File > Export menu

1. Select one or more Point Cloud objects in the 3D Viewport.
2. Go to **File > Export** and choose the desired format:
   - **Point Cloud (.ply)**
   - **Gaussian Splat (.ply)**
   - **Gaussian Splat (.splat)**
3. Set options in the sidebar and click **Export**.

### Exporters Panel (Blender 4.2+)

1. Link Point Cloud objects to a collection.
2. Open **Collection Properties > Exporters**.
3. Add an exporter entry and select the desired format.
4. Set the output path and options once; re-export at any time with a single click.

---

## Compatibility

Requires **Blender 4.2** or newer.
