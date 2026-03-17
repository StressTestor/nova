"""
Convert MakeHuman base mesh to NOVA holographic head.
1. Import full body OBJ, crop to head + upper shoulders
2. Delete ALL interior geometry (teeth, tongue, eyeballs, eyelashes)
   by keeping only the largest connected mesh island
3. Close the mouth opening
4. Push proportions toward anime (bigger eyes, smaller nose/mouth, sharper chin)
5. Generate stylized hair volume
6. Decimate, center, export as GLB

Usage: blender --background --python scripts/convert_head.py
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector

INPUT_OBJ = "/tmp/makehuman_base.obj"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_GLB = os.path.join(SCRIPT_DIR, "..", "src", "assets", "models", "holo_head.glb")
TARGET_FACES = 3500

# ── CLEAN SCENE ──────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=INPUT_OBJ)

obj = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# ── STEP 1: CROP TO HEAD + UPPER SHOULDERS ───────────────────
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()

max_y = max(v.co.y for v in bm.verts)
min_y = min(v.co.y for v in bm.verts)
total_height = max_y - min_y
cutoff = max_y - total_height * 0.22

verts_to_del = [v for v in bm.verts if v.co.y < cutoff]
print(f"Cropping: deleting {len(verts_to_del)} of {len(bm.verts)} vertices below Y={cutoff:.2f}")
bmesh.ops.delete(bm, geom=verts_to_del, context='VERTS')

# Remove loose
loose = [v for v in bm.verts if not v.link_edges]
if loose:
    bmesh.ops.delete(bm, geom=loose, context='VERTS')

bm.to_mesh(obj.data)
bm.free()
print(f"After crop: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")

# ── STEP 2: DELETE ALL INTERIOR GEOMETRY ─────────────────────
# Keep only the largest connected mesh island (the head surface)
# This removes teeth, tongue, eyeballs, eyelashes, inner mouth cavity
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
print(f"Found {len(islands)} mesh islands. Largest: {len(islands[0])} verts")

# Delete all islands except the largest
verts_to_remove = []
for island in islands[1:]:
    for idx in island:
        verts_to_remove.append(bm.verts[idx])

print(f"Removing {len(verts_to_remove)} interior/detail vertices ({len(islands)-1} islands)")
bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')

# Remove any new loose verts
bm.verts.ensure_lookup_table()
loose = [v for v in bm.verts if not v.link_edges]
if loose:
    bmesh.ops.delete(bm, geom=loose, context='VERTS')

bm.to_mesh(obj.data)
bm.free()
print(f"After interior cleanup: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")

# ── STEP 3: CLOSE OPENINGS ──────────────────────────────────
# Find boundary edges (edges with only 1 face) and fill them
# This closes the mouth, eye sockets, nostrils, and chest cutoff
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.edges.ensure_lookup_table()

# Find boundary edge loops
boundary_edges = [e for e in bm.edges if len(e.link_faces) == 1]
print(f"Boundary edges to close: {len(boundary_edges)}")

# Select boundary edges and fill
for e in boundary_edges:
    e.select = True

bm.to_mesh(obj.data)
bm.free()

# Use Blender's fill operation on selected edges
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_mode(type='EDGE')
# Select boundary edges
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_non_manifold()
bpy.ops.mesh.fill()
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

print(f"After closing openings: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")

# ── STEP 4: ANIME PROPORTIONS ───────────────────────────────
# Push proportions toward anime style:
# - Scale eyes up 15-20%
# - Reduce nose/mouth size
# - Sharpen chin taper
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()

# Reference points from mesh inspection:
# Eyes: Y ~7.0-7.5, X ~+-0.35, Z > 1.0
# Nose: Y ~6.5-7.0, X ~0, Z > 1.0
# Mouth: Y ~6.0-6.5, X ~+-0.3, Z > 0.8
# Chin: Y < 6.0
# Head center: Y ~6.36, Z ~0.84

head_center_y = sum(v.co.y for v in bm.verts) / len(bm.verts)
front_z = max(v.co.z for v in bm.verts)

for v in bm.verts:
    x, y, z = v.co.x, v.co.y, v.co.z

    # ── EYES: Scale outward from eye center to enlarge 18% ──
    for side in [-1, 1]:
        eye_cx = 0.35 * side
        eye_cy = 7.3
        eye_cz = 1.3
        dx = x - eye_cx
        dy = y - eye_cy
        dz = z - eye_cz
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 0.4:
            # Scale outward from eye center
            scale = 1.0 + 0.18 * max(0, 1.0 - dist / 0.4)
            v.co.x = eye_cx + dx * scale
            v.co.y = eye_cy + dy * scale
            v.co.z = eye_cz + dz * scale
            break

    # ── NOSE: Scale down toward nose center ──
    nose_cx, nose_cy, nose_cz = 0.0, 6.8, 1.4
    dx = x - nose_cx
    dy = y - nose_cy
    dz = z - nose_cz
    nose_dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    if nose_dist < 0.3 and abs(x) < 0.2:
        shrink = 1.0 - 0.15 * max(0, 1.0 - nose_dist / 0.3)
        v.co.x = nose_cx + dx * shrink
        v.co.z = nose_cz + dz * shrink

    # ── MOUTH: Scale down toward mouth center ──
    mouth_cx, mouth_cy, mouth_cz = 0.0, 6.3, 1.3
    dx = x - mouth_cx
    dy = y - mouth_cy
    dz = z - mouth_cz
    mouth_dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    if mouth_dist < 0.3 and abs(x) < 0.4:
        shrink = 1.0 - 0.12 * max(0, 1.0 - mouth_dist / 0.3)
        v.co.x = mouth_cx + dx * shrink

    # ── CHIN: Sharpen V-taper ──
    if y < 6.0:
        t = (6.0 - y) / 1.2  # How far below mouth
        t = min(1.0, max(0.0, t))
        # Squeeze X inward for chin taper
        v.co.x *= 1.0 - t * 0.2
        # Bring chin forward slightly
        if abs(x) < 0.3:
            v.co.z += t * 0.08

bm.to_mesh(obj.data)
bm.free()
print("Applied anime proportions: enlarged eyes, reduced nose/mouth, sharpened chin")

# ── STEP 5: SMOOTH ──────────────────────────────────────────
bpy.ops.object.shade_smooth()

# Light smooth to blend the proportion changes
smooth = obj.modifiers.new(name="Smooth", type='SMOOTH')
smooth.factor = 0.3
smooth.iterations = 3
bpy.ops.object.modifier_apply(modifier="Smooth")

# ── STEP 6: ADD HAIR ────────────────────────────────────────
# Create anime-style hair as a separate mesh, then join
# Hair components: main volume cap, side-swept bangs, back flow

def create_hair():
    """Create stylized anime hair volume."""
    hair_objects = []

    # Reference: head top is around Y=8.5, back of head Z~-0.5
    # Hair should sit on top and flow down the back

    # ── MAIN HAIR CAP (top of head) ──
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16,
        radius=1.0, location=(0, 7.8, 0.5)
    )
    cap = bpy.context.active_object
    cap.name = "HairCap"

    # Shape: wider on sides, flatter on top, elongated backward
    cap.scale = (1.15, 0.65, 0.95)
    bpy.ops.object.transform_apply(scale=True)

    # Sculpt the cap to hug the head shape
    bm_cap = bmesh.new()
    bm_cap.from_mesh(cap.data)
    bm_cap.verts.ensure_lookup_table()
    for v in bm_cap.verts:
        # Remove bottom half (sits on head)
        if v.co.y < -0.1:
            v.co.y = -0.1 - (v.co.y + 0.1) * 0.2
        # Push back vertices further back
        if v.co.z < 0:
            v.co.z *= 1.3
    bm_cap.to_mesh(cap.data)
    bm_cap.free()
    hair_objects.append(cap)

    # ── SIDE SWEPT BANGS (anime front hair) ──
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=10,
        radius=0.6, location=(0.3, 7.5, 1.3)
    )
    bangs = bpy.context.active_object
    bangs.name = "HairBangs"
    bangs.scale = (0.9, 0.5, 0.4)
    bpy.ops.object.transform_apply(scale=True)

    # Shape bangs: sweep to the right, taper downward
    bm_b = bmesh.new()
    bm_b.from_mesh(bangs.data)
    bm_b.verts.ensure_lookup_table()
    for v in bm_b.verts:
        # Sweep to right side
        if v.co.y < 0:
            v.co.x += abs(v.co.y) * 0.3
        # Taper toward tips
        if v.co.y < -0.15:
            t = abs(v.co.y + 0.15) / 0.3
            v.co.x *= 1.0 - t * 0.3
            v.co.z *= 1.0 - t * 0.4
    bm_b.to_mesh(bangs.data)
    bm_b.free()
    hair_objects.append(bangs)

    # ── LEFT SIDE HAIR STRAND ──
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8,
        radius=0.35, location=(-0.8, 7.2, 0.8)
    )
    left_strand = bpy.context.active_object
    left_strand.name = "HairLeftStrand"
    left_strand.scale = (0.4, 0.7, 0.35)
    bpy.ops.object.transform_apply(scale=True)

    bm_ls = bmesh.new()
    bm_ls.from_mesh(left_strand.data)
    bm_ls.verts.ensure_lookup_table()
    for v in bm_ls.verts:
        if v.co.y < 0:
            t = abs(v.co.y) / 0.5
            v.co.x -= t * 0.15
            v.co.x *= 1.0 - t * 0.4
    bm_ls.to_mesh(left_strand.data)
    bm_ls.free()
    hair_objects.append(left_strand)

    # ── BACK HAIR (long, flowing down) ──
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=14,
        radius=1.0, location=(0, 7.0, -0.3)
    )
    back = bpy.context.active_object
    back.name = "HairBack"
    back.scale = (0.9, 1.4, 0.5)
    bpy.ops.object.transform_apply(scale=True)

    # Shape: flow downward, taper into strands at tips
    bm_back = bmesh.new()
    bm_back.from_mesh(back.data)
    bm_back.verts.ensure_lookup_table()
    for v in bm_back.verts:
        # Remove front half
        if v.co.z > 0.2:
            v.co.z = 0.2
        # Extend downward
        if v.co.y < -0.3:
            t = abs(v.co.y + 0.3) / 1.0
            t = min(1.0, t)
            # Strand taper at tips
            strand_freq = 6
            strand_phase = math.atan2(v.co.x, v.co.z) * strand_freq
            strand_mod = 0.5 + 0.5 * math.sin(strand_phase)
            taper = 1.0 - t * (0.3 + strand_mod * 0.5)
            v.co.x *= max(0.15, taper)
            v.co.z *= max(0.15, taper)
            # Flow backward as it goes down
            v.co.z -= t * 0.3
    bm_back.to_mesh(back.data)
    bm_back.free()
    hair_objects.append(back)

    # ── RIGHT SIDE LONG STRAND ──
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8,
        radius=0.3, location=(0.9, 7.0, 0.5)
    )
    right_strand = bpy.context.active_object
    right_strand.name = "HairRightStrand"
    right_strand.scale = (0.3, 0.8, 0.3)
    bpy.ops.object.transform_apply(scale=True)

    bm_rs = bmesh.new()
    bm_rs.from_mesh(right_strand.data)
    bm_rs.verts.ensure_lookup_table()
    for v in bm_rs.verts:
        if v.co.y < 0:
            t = abs(v.co.y) / 0.6
            v.co.x += t * 0.1
            v.co.x *= 1.0 - t * 0.3
    bm_rs.to_mesh(right_strand.data)
    bm_rs.free()
    hair_objects.append(right_strand)

    return hair_objects

hair_parts = create_hair()

# ── STEP 7: JOIN ALL OBJECTS ─────────────────────────────────
bpy.ops.object.select_all(action='DESELECT')
for h in hair_parts:
    h.select_set(True)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.join()
print(f"After joining hair: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")

# ── STEP 8: DECIMATE ─────────────────────────────────────────
current_faces = len(obj.data.polygons)
if current_faces > TARGET_FACES:
    ratio = TARGET_FACES / current_faces
    dec = obj.modifiers.new(name="Decimate", type='DECIMATE')
    dec.ratio = ratio
    bpy.ops.object.modifier_apply(modifier="Decimate")
    print(f"Decimated: {current_faces} -> {len(obj.data.polygons)} faces (ratio {ratio:.3f})")

# ── STEP 9: CENTER AND SCALE ─────────────────────────────────
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
obj.location = (0, 0, 0)

# Scale so head is ~2 units tall
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()
ys = [v.co.y for v in bm.verts]
current_height = max(ys) - min(ys)
bm.free()

if current_height > 0:
    scale = 2.0 / current_height
    obj.scale = (scale, scale, scale)
    bpy.ops.object.transform_apply(scale=True)
    print(f"Scaled by {scale:.3f}")

# Smooth normals
bpy.ops.object.shade_smooth()

# Remove materials
obj.data.materials.clear()

# ── STEP 10: EXPORT ──────────────────────────────────────────
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
print(f"  NOVA Head exported (MakeHuman CC0 + anime mods + hair)")
print(f"  Path:     {OUTPUT_GLB}")
print(f"  Faces:    {final_f}")
print(f"  Vertices: {final_v}")
print(f"  Features: No interior mouth geometry")
print(f"            Anime proportions (eyes +18%, nose/mouth reduced)")
print(f"            Stylized hair volume (5 pieces)")
print(f"            Fresnel-weighted wireframe compatible")
print(f"{'='*60}")
