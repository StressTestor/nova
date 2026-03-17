"""
Convert MakeHuman base mesh to NOVA holographic head.

Fixes applied:
1. Delete ALL interior mouth geometry (cavity, teeth, tongue on main island)
2. Tight collarbone crop (top 15% of body, no wide shoulders)
3. Remove all disconnected/floating pieces, loose verts/edges
4. No anime proportions — realistic female head, shader handles stylization
5. Target 2000-3000 faces

Usage: blender --background --python scripts/convert_head.py
Requires: /tmp/makehuman_base.obj (download from MakeHuman GitHub)
"""

import bpy
import bmesh
import os
from mathutils import Vector

INPUT_OBJ = "/tmp/makehuman_base.obj"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_GLB = os.path.join(SCRIPT_DIR, "..", "src", "assets", "models", "holo_head.glb")
TARGET_FACES = 2500

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=INPUT_OBJ)

obj = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj


# ═══════════════════════════════════════════════════════════════
# STEP 1: Crop to head + neck + collarbone (top 15% of body)
# At 15%, max |X| is ~1.7 — tight bust, no arms
# ═══════════════════════════════════════════════════════════════

bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()

max_y = max(v.co.y for v in bm.verts)
min_y = min(v.co.y for v in bm.verts)
total_height = max_y - min_y
y_cutoff = max_y - total_height * 0.15

to_del = [v for v in bm.verts if v.co.y < y_cutoff]
print(f"Step 1: Cropping below Y={y_cutoff:.2f} — removing {len(to_del)} verts")
bmesh.ops.delete(bm, geom=to_del, context='VERTS')

# Also clip any vertices wider than |X| > 2.0 (stray shoulder geometry)
bm.verts.ensure_lookup_table()
wide = [v for v in bm.verts if abs(v.co.x) > 2.0]
if wide:
    print(f"  Clipping {len(wide)} wide vertices (|X| > 2.0)")
    bmesh.ops.delete(bm, geom=wide, context='VERTS')

# Remove loose
bm.verts.ensure_lookup_table()
loose = [v for v in bm.verts if not v.link_edges]
if loose:
    bmesh.ops.delete(bm, geom=loose, context='VERTS')

bm.to_mesh(obj.data)
bm.free()
print(f"  After crop: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")


# ═══════════════════════════════════════════════════════════════
# STEP 2: Delete all non-main mesh islands
# Removes: teeth, tongue, eyeballs, eyelashes, separate body parts
# ═══════════════════════════════════════════════════════════════

bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()

visited = set()
islands = []

def flood_fill(start):
    component = set()
    stack = [start]
    while stack:
        v = stack.pop()
        if v.index in visited:
            continue
        visited.add(v.index)
        component.add(v.index)
        for e in v.link_edges:
            other = e.other_vert(v)
            if other.index not in visited:
                stack.append(other)
    return component

for v in bm.verts:
    if v.index not in visited:
        islands.append(flood_fill(v))

islands.sort(key=len, reverse=True)
print(f"Step 2: Found {len(islands)} mesh islands — keeping largest ({len(islands[0])} verts)")

verts_to_remove = []
for island in islands[1:]:
    for idx in island:
        verts_to_remove.append(bm.verts[idx])

if verts_to_remove:
    print(f"  Removing {len(verts_to_remove)} verts from {len(islands)-1} non-main islands")
    bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')

bm.verts.ensure_lookup_table()
loose = [v for v in bm.verts if not v.link_edges]
if loose:
    bmesh.ops.delete(bm, geom=loose, context='VERTS')

bm.to_mesh(obj.data)
bm.free()
print(f"  After island cleanup: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")


# ═══════════════════════════════════════════════════════════════
# STEP 3: Delete mouth interior faces on the main island
# The mouth cavity is CONNECTED to the skin surface at the lip edges.
# Identify interior faces by: faces in the mouth region whose normals
# point TOWARD the head center (inward-facing).
# ═══════════════════════════════════════════════════════════════

bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# Compute head center
n = len(bm.verts)
hc = Vector((
    sum(v.co.x for v in bm.verts) / n,
    sum(v.co.y for v in bm.verts) / n,
    sum(v.co.z for v in bm.verts) / n,
))
print(f"Step 3: Head center at ({hc.x:.2f}, {hc.y:.2f}, {hc.z:.2f})")

# Find the front Z surface at mouth height — faces at ~Y=6.0-6.7, near center
front_faces_z = []
for f in bm.faces:
    fc = f.calc_center_median()
    if 6.0 < fc.y < 6.7 and abs(fc.x) < 0.4 and f.normal.z > 0.1:
        front_faces_z.append(fc.z)

if front_faces_z:
    lip_z = sorted(front_faces_z)[-len(front_faces_z)//4]  # 75th percentile
    print(f"  Lip line Z (approx): {lip_z:.2f}")
else:
    lip_z = 1.2
    print(f"  Lip line Z (fallback): {lip_z:.2f}")

# Interior mouth faces: in mouth region, center behind lip line,
# and normal points toward head center (inward)
mouth_interior = []
for f in bm.faces:
    fc = f.calc_center_median()
    # Mouth region bounds
    if not (5.9 < fc.y < 6.9 and abs(fc.x) < 0.5):
        continue
    # Behind the lip surface
    if fc.z > lip_z - 0.05:
        continue
    # Normal points inward — dot product with (face_center → head_center) is positive
    to_center = hc - fc
    if to_center.length > 0 and f.normal.dot(to_center.normalized()) > 0.15:
        mouth_interior.append(f)

print(f"  Found {len(mouth_interior)} mouth interior faces to delete")
if mouth_interior:
    bmesh.ops.delete(bm, geom=mouth_interior, context='FACES')

# Also check for any remaining deeply interior faces anywhere
# (nasal cavity, eye socket interior, etc.)
bm.faces.ensure_lookup_table()
bm.verts.ensure_lookup_table()
n = len(bm.verts)
if n > 0:
    hc2 = Vector((
        sum(v.co.x for v in bm.verts) / n,
        sum(v.co.y for v in bm.verts) / n,
        sum(v.co.z for v in bm.verts) / n,
    ))
    deep_interior = []
    for f in bm.faces:
        fc = f.calc_center_median()
        to_center = hc2 - fc
        dist_from_center = to_center.length
        # Face very close to center AND pointing inward = interior
        if dist_from_center < 0.5 and f.normal.dot(to_center.normalized()) > 0.3:
            deep_interior.append(f)
    if deep_interior:
        print(f"  Removing {len(deep_interior)} additional deep interior faces")
        bmesh.ops.delete(bm, geom=deep_interior, context='FACES')

bm.to_mesh(obj.data)
bm.free()
print(f"  After mouth cleanup: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")


# ═══════════════════════════════════════════════════════════════
# STEP 4: Close all boundary openings
# Fill holes left by mouth cleanup, eye sockets, nostrils, chest cutoff
# ═══════════════════════════════════════════════════════════════

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_mode(type='EDGE')
bpy.ops.mesh.select_non_manifold()
bpy.ops.mesh.fill()
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

print(f"Step 4: After closing openings: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")


# ═══════════════════════════════════════════════════════════════
# STEP 4b: Add hair volume
# Simple swept-back shell that wraps the back/top of the head.
# Works in original MakeHuman coordinates (Y up, head top ~8.5).
# ═══════════════════════════════════════════════════════════════

import math

# Create a UV sphere for the hair shell
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=18, ring_count=12,
    radius=1.1, location=(0, 7.6, 0.3)
)
hair = bpy.context.active_object
hair.name = "Hair"

# Scale to wrap the head: wider on sides, elongated backward and down
hair.scale = (1.05, 0.75, 0.85)
bpy.ops.object.transform_apply(scale=True)

bm_h = bmesh.new()
bm_h.from_mesh(hair.data)
bm_h.verts.ensure_lookup_table()

for v in bm_h.verts:
    x, y, z = v.co.x, v.co.y, v.co.z

    # Poofy top
    if y > 0.2:
        t = (y - 0.2) / 0.6
        x *= 1.0 + t * 0.08
        z *= 1.0 + t * 0.05

    # Back hair flows down further
    if z < -0.1:
        back_t = min(1.0, max(0, (-0.1 - z) / 0.6))
        y -= back_t * 0.6  # extend downward
        x *= 1.0 + back_t * 0.03

    # Hair tips taper into strands
    if y < -0.5:
        t = min(1.0, max(0, (-0.5 - y) / 0.5))
        angle = math.atan2(x, z)
        strand = 0.5 + 0.5 * math.sin(angle * 6.0)
        taper = 1.0 - t * (0.25 + strand * 0.45)
        x *= max(0.12, taper)
        z *= max(0.12, taper)

    v.co.x = x
    v.co.y = y
    v.co.z = z

# Delete front-lower vertices where the face shows through
verts_remove = []
bm_h.verts.ensure_lookup_table()
for v in bm_h.verts:
    # Face area: front (z > 0.3), below forehead (y < 0.25), within face width
    if v.co.z > 0.3 and v.co.y < 0.25 and abs(v.co.x) < 0.55:
        # But keep the bangs (top-front)
        if not (v.co.y > 0.05 and v.co.z > 0.5):
            verts_remove.append(v)
    # Also remove bottom-interior verts
    if v.co.y < -0.9 and abs(v.co.x) < 0.2 and v.co.z > 0:
        verts_remove.append(v)

if verts_remove:
    bmesh.ops.delete(bm_h, geom=verts_remove, context='VERTS')

# Light smooth
bm_h.verts.ensure_lookup_table()
for _ in range(2):
    offsets = {}
    for v in bm_h.verts:
        if not v.link_edges:
            continue
        neighbors = [e.other_vert(v).co.copy() for e in v.link_edges]
        if neighbors:
            avg = sum(neighbors, Vector((0, 0, 0))) / len(neighbors)
            offsets[v.index] = (avg - v.co) * 0.2
    for v in bm_h.verts:
        if v.index in offsets:
            v.co += offsets[v.index]

bm_h.to_mesh(hair.data)
bm_h.free()

bpy.ops.object.shade_smooth()
hair_faces = len(hair.data.polygons)
print(f"Step 4b: Added hair volume ({hair_faces} faces)")

# Join hair to head
bpy.ops.object.select_all(action='DESELECT')
hair.select_set(True)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.join()
print(f"  After join: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")


# ═══════════════════════════════════════════════════════════════
# STEP 5: Decimate to target face count
# ═══════════════════════════════════════════════════════════════

current_faces = len(obj.data.polygons)
if current_faces > TARGET_FACES:
    ratio = TARGET_FACES / current_faces
    dec = obj.modifiers.new(name="Decimate", type='DECIMATE')
    dec.ratio = ratio
    bpy.ops.object.modifier_apply(modifier="Decimate")
    print(f"Step 5: Decimated {current_faces} → {len(obj.data.polygons)} faces (ratio {ratio:.3f})")
else:
    print(f"Step 5: Already at {current_faces} faces, no decimation needed")


# ═══════════════════════════════════════════════════════════════
# STEP 6: Final cleanup — remove ANY loose/disconnected geometry
# Run this AFTER decimation since decimate can create loose pieces
# ═══════════════════════════════════════════════════════════════

bm = bmesh.new()
bm.from_mesh(obj.data)

# Remove loose vertices (no edges)
loose_v = [v for v in bm.verts if not v.link_edges]
if loose_v:
    print(f"Step 6: Removing {len(loose_v)} loose vertices")
    bmesh.ops.delete(bm, geom=loose_v, context='VERTS')

# Remove loose edges (no faces)
bm.edges.ensure_lookup_table()
loose_e = [e for e in bm.edges if not e.link_faces]
if loose_e:
    print(f"  Removing {len(loose_e)} loose edges")
    bmesh.ops.delete(bm, geom=loose_e, context='EDGES')

# Remove any small disconnected islands created by decimation
bm.verts.ensure_lookup_table()
visited = set()
post_islands = []

for v in bm.verts:
    if v.index not in visited:
        component = set()
        stack = [v]
        while stack:
            curr = stack.pop()
            if curr.index in visited:
                continue
            visited.add(curr.index)
            component.add(curr.index)
            for e in curr.link_edges:
                other = e.other_vert(curr)
                if other.index not in visited:
                    stack.append(other)
        post_islands.append(component)

post_islands.sort(key=len, reverse=True)
if len(post_islands) > 1:
    remove_verts = []
    for island in post_islands[1:]:
        for idx in island:
            remove_verts.append(bm.verts[idx])
    print(f"  Removing {len(remove_verts)} verts from {len(post_islands)-1} post-decimate islands")
    bmesh.ops.delete(bm, geom=remove_verts, context='VERTS')

bm.to_mesh(obj.data)
bm.free()


# ═══════════════════════════════════════════════════════════════
# STEP 7: Center, scale, smooth, export
# ═══════════════════════════════════════════════════════════════

bpy.ops.object.shade_smooth()
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
obj.location = (0, 0, 0)

# Scale so head is ~2 units tall
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()
ys = [v.co.y for v in bm.verts]
h = max(ys) - min(ys)
bm.free()

if h > 0:
    s = 2.0 / h
    obj.scale = (s, s, s)
    bpy.ops.object.transform_apply(scale=True)

obj.data.materials.clear()

os.makedirs(os.path.dirname(OUTPUT_GLB), exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_normals=True,
    export_materials='NONE',
    export_yup=True,
)

final_f = len(obj.data.polygons)
final_v = len(obj.data.vertices)
print(f"\n{'='*60}")
print(f"  NOVA Head — MakeHuman CC0 base, cleaned")
print(f"  Path:     {OUTPUT_GLB}")
print(f"  Faces:    {final_f}")
print(f"  Vertices: {final_v}")
print(f"  Crop:     Head + neck + collarbone (top 15%)")
print(f"  Interior: Mouth cavity removed, openings filled")
print(f"  Islands:  Single connected mesh, no floaters")
print(f"{'='*60}")
