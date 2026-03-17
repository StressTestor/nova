"""
Convert MakeHuman base mesh to NOVA holographic head.
- Import full body OBJ
- Delete everything below upper chest
- Decimate to ~3000 faces
- Center, smooth, export as GLB

Usage: blender --background --python scripts/convert_head.py
"""

import bpy
import bmesh
import os

INPUT_OBJ = "/tmp/makehuman_base.obj"
OUTPUT_GLB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "assets", "models", "holo_head.glb")
TARGET_FACES = 3000

# Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import OBJ
bpy.ops.wm.obj_import(filepath=INPUT_OBJ)

# Get the imported object
obj = None
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        obj = o
        break

if obj is None:
    print("ERROR: No mesh found after import")
    exit(1)

# Select and activate
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Determine head cutoff height
# MakeHuman base mesh: head is at the top, Y is up in OBJ
# Let's find the vertex height range to determine the cutoff
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()

# Get Y (height) range
heights = [v.co.y for v in bm.verts]
# In some OBJ exports, Z might be up instead of Y
# Let's check which axis has the largest range
x_range = max(v.co.x for v in bm.verts) - min(v.co.x for v in bm.verts)
y_range = max(v.co.y for v in bm.verts) - min(v.co.y for v in bm.verts)
z_range = max(v.co.z for v in bm.verts) - min(v.co.z for v in bm.verts)

print(f"Axis ranges: X={x_range:.2f}, Y={y_range:.2f}, Z={z_range:.2f}")

# The tallest axis is the up axis
if y_range >= z_range and y_range >= x_range:
    up_axis = 'Y'
    up_fn = lambda v: v.co.y
elif z_range >= y_range and z_range >= x_range:
    up_axis = 'Z'
    up_fn = lambda v: v.co.z
else:
    up_axis = 'X'
    up_fn = lambda v: v.co.x

print(f"Up axis detected: {up_axis}")

heights = [up_fn(v) for v in bm.verts]
min_h = min(heights)
max_h = max(heights)
total_height = max_h - min_h

print(f"Height range: {min_h:.2f} to {max_h:.2f} (total: {total_height:.2f})")

# Keep top 20% of the body (head + neck + upper shoulders)
# MakeHuman body proportions: head is roughly top 12-15% of total height
# We want head + neck + upper shoulders = ~20-25%
cutoff = max_h - (total_height * 0.22)
print(f"Cutoff height: {cutoff:.2f} (keeping top 22%)")

# Delete vertices below cutoff
verts_to_delete = [v for v in bm.verts if up_fn(v) < cutoff]
print(f"Deleting {len(verts_to_delete)} of {len(bm.verts)} vertices")

bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')

# Remove loose vertices
loose = [v for v in bm.verts if not v.link_edges]
if loose:
    bmesh.ops.delete(bm, geom=loose, context='VERTS')

bm.to_mesh(obj.data)
bm.free()

remaining_faces = len(obj.data.polygons)
print(f"Remaining faces after crop: {remaining_faces}")

# Decimate if needed
if remaining_faces > TARGET_FACES:
    ratio = TARGET_FACES / remaining_faces
    dec = obj.modifiers.new(name="Decimate", type='DECIMATE')
    dec.ratio = ratio
    bpy.ops.object.modifier_apply(modifier="Decimate")
    print(f"Decimated with ratio {ratio:.3f}")

# Smooth normals
bpy.ops.object.shade_smooth()

# Center the object
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
obj.location = (0, 0, 0)

# Scale to reasonable size (head should be roughly 2 units tall)
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()

current_heights = [up_fn(v) for v in bm.verts]
current_height = max(current_heights) - min(current_heights)
bm.free()

if current_height > 0:
    scale_factor = 2.0 / current_height
    obj.scale = (scale_factor, scale_factor, scale_factor)
    bpy.ops.object.transform_apply(scale=True)
    print(f"Scaled by {scale_factor:.3f} (head height now ~2 units)")

# Remove any materials
obj.data.materials.clear()

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_GLB), exist_ok=True)

# Select only our object for export
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)

# Export as GLB
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_normals=True,
    export_materials='NONE',
    export_yup=True,
)

final_faces = len(obj.data.polygons)
final_verts = len(obj.data.vertices)
print(f"\n{'='*55}")
print(f"  NOVA Head (MakeHuman base) exported")
print(f"  Path:     {OUTPUT_GLB}")
print(f"  Faces:    {final_faces}")
print(f"  Vertices: {final_verts}")
print(f"  Source:   MakeHuman base mesh (CC0)")
print(f"{'='*55}")
