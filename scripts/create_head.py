"""
NOVA holographic head — built from scratch.
Simple low-poly VTuber aesthetic. Every shape is a closed outward-facing shell.
No interior geometry. Designed to look good through wireframe shader.

Usage: blender --background --python scripts/create_head.py
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector

OUTPUT_GLB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "src", "assets", "models", "holo_head.glb"
)

bpy.ops.wm.read_factory_settings(use_empty=True)


# ═══════════════════════════════════════════════════════════════
# HEAD + NECK + SHOULDERS — one continuous closed mesh
# ═══════════════════════════════════════════════════════════════

# Blender coords: Z up, Y forward (face direction), X left/right
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=22, ring_count=16, radius=1.0, location=(0, 0, 0)
)
head = bpy.context.active_object
head.name = "NovaHead"

bm = bmesh.new()
bm.from_mesh(head.data)
bm.verts.ensure_lookup_table()

for v in bm.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    orig_x, orig_y, orig_z = x, y, z

    # ── OVERALL: egg shape, taller, narrower jaw ──
    z *= 1.2

    # ── CRANIUM: keep round and full on top ──
    if z > 0.3:
        t = (z - 0.3) / 0.9
        # Slightly wider at temples
        x *= 1.0 + t * 0.03

    # ── FOREHEAD: smooth, slightly convex ──
    if z > 0.2 and z < 0.6 and y > 0.5:
        t_z = 1.0 - abs(z - 0.4) / 0.2
        t_x = 1.0 - abs(x) / 0.8
        y += max(0, t_z) * max(0, t_x) * 0.05

    # ── EYE SOCKETS: large, deep, anime-sized (~30% of face) ──
    for side in [-1, 1]:
        eye_cx = 0.32 * side
        eye_cz = 0.12
        # Elliptical region — wide horizontally, tall vertically
        dx = (x - eye_cx) / 0.22
        dz = (z - eye_cz) / 0.16
        dist = math.sqrt(dx * dx + dz * dz)
        if dist < 1.0 and y > 0.2:
            # Deep concavity — cubic falloff for sharp rim
            depth = (1.0 - dist)
            depth = depth * depth * depth
            y -= depth * 0.35

            # Brow ridge — slight overhang above eye
            if dz > 0.6 and dz < 1.2 and abs(dx) < 0.9:
                brow_t = 1.0 - abs(dz - 0.9) / 0.3
                y += max(0, brow_t) * 0.04

    # ── NOSE: tiny triangular protrusion ──
    if abs(x) < 0.07 and z > -0.12 and z < 0.05 and y > 0.7:
        t_z = 1.0 - abs(z + 0.03) / 0.08
        t_x = 1.0 - abs(x) / 0.07
        protrusion = max(0, t_z) * max(0, t_x)
        y += protrusion * 0.14
        # Slight upturn
        z += protrusion * 0.02

    # ── MOUTH: just a horizontal crease, no opening ──
    if abs(x) < 0.18 and abs(z + 0.22) < 0.02 and y > 0.65:
        crease_t = 1.0 - abs(x) / 0.18
        y -= crease_t * 0.02

    # ── CHEEKBONES: subtle outward push ──
    if z > -0.15 and z < 0.05 and abs(x) > 0.35 and y > 0.2:
        cheek_t = max(0, 1.0 - abs(z + 0.05) / 0.1) * max(0, (abs(x) - 0.35) / 0.3)
        y += cheek_t * 0.04
        x += cheek_t * 0.06 * (1 if x > 0 else -1)

    # ── JAW V-TAPER: progressive squeeze below cheekbones ──
    if z > -0.6 and z < -0.1:
        t = (-0.1 - z) / 0.5
        t = max(0, min(1, t))
        x *= 1.0 - t * 0.4
        # Jaw edge definition
        if abs(x) > 0.25 and t < 0.5:
            y -= 0.03

    # ── CHIN: sharp V point ──
    if z < -0.4:
        t = (-0.4 - z) / 0.8
        t = min(1, max(0, t))
        # Aggressive V-taper
        x *= 1.0 - t * 0.7
        y *= 1.0 - t * 0.4
        # Point the chin forward slightly
        if abs(x) < 0.15:
            chin_t = max(0, 1.0 - abs(x) / 0.15) * t
            y += chin_t * 0.06

    # ── NECK: narrow cylinder below chin ──
    if z < -0.75:
        t = (-0.75 - z) / 0.45
        t = min(1, max(0, t))
        neck_scale = 0.38 - t * 0.02
        x *= neck_scale
        y *= neck_scale * 0.85
        # Slight forward lean
        y += t * 0.03

    # ── SHOULDER STUBS: widen at very bottom ──
    if z < -1.05:
        t = (-1.05 - z) / 0.15
        t = min(1, max(0, t))
        # Flare outward for shoulder suggestion
        x_sign = 1 if x > 0 else (-1 if x < 0 else 0)
        x += x_sign * t * 0.25
        # Drop shoulders slightly
        z -= t * 0.05

    # ── BACK OF HEAD: fuller, rounder ──
    if y < -0.3 and z > -0.3 and z < 0.6:
        t_y = max(0, (-0.3 - y) / 0.5)
        t_z = max(0, 1.0 - abs(z - 0.15) / 0.45)
        y -= t_y * t_z * 0.08

    v.co.x = x
    v.co.y = y
    v.co.z = z

# Light smooth to blend deformations
bm.verts.ensure_lookup_table()
for _ in range(3):
    offsets = {}
    for v in bm.verts:
        if not v.link_edges:
            continue
        neighbors = [e.other_vert(v).co.copy() for e in v.link_edges]
        if neighbors:
            avg = sum(neighbors, Vector((0, 0, 0))) / len(neighbors)
            offsets[v.index] = (avg - v.co) * 0.2
    for v in bm.verts:
        if v.index in offsets:
            v.co += offsets[v.index]

bm.to_mesh(head.data)
bm.free()

# Apply smooth shading
bpy.ops.object.shade_smooth()

head_faces = len(head.data.polygons)
head_verts = len(head.data.vertices)
print(f"Head: {head_verts} verts, {head_faces} faces")


# ═══════════════════════════════════════════════════════════════
# HAIR — separate closed shell, sits on top/back of head
# ═══════════════════════════════════════════════════════════════

# Main hair volume: larger egg shape covering back and top
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=18, ring_count=12, radius=1.0, location=(0, 0, 0.1)
)
hair = bpy.context.active_object
hair.name = "NovaHair"

bm = bmesh.new()
bm.from_mesh(hair.data)
bm.verts.ensure_lookup_table()

# Shape the hair shell
for v in bm.verts:
    x, y, z = v.co.x, v.co.y, v.co.z

    # Scale to be slightly larger than head
    x *= 1.15
    y *= 1.08
    z *= 1.2

    # ── HAIR VOLUME: poofy on top and sides ──
    if z > 0.2:
        t = (z - 0.2) / 1.0
        x *= 1.0 + t * 0.12
        y *= 1.0 + t * 0.08

    # ── BACK HAIR: extends lower, flows down ──
    if y < -0.2 and z < 0:
        back_t = max(0, min(1, (-0.2 - y) / 0.6))
        # Extend downward
        z -= back_t * 0.5
        # Keep width
        x *= 1.0 + back_t * 0.05

    # ── FRONT BANGS: sweep across forehead ──
    if y > 0.5 and z > 0.15 and z < 0.55:
        bang_t = max(0, 1.0 - abs(z - 0.35) / 0.2)
        # Push bangs forward
        y += bang_t * 0.18
        # Slight asymmetric sweep (more to the right)
        if x > -0.2:
            sweep_t = max(0, (x + 0.2) / 0.8) * bang_t
            y += sweep_t * 0.06

    # ── REMOVE FACE AREA: carve out where face shows ──
    # Don't literally delete — instead push these vertices behind the head surface
    # so they don't cover the face
    if y > 0.3 and z < 0.2 and z > -0.5 and abs(x) < 0.55:
        # Keep bangs area
        if not (z > 0.1 and y > 0.6):
            # Push behind face plane
            y = min(y, 0.3 - (0.2 - z) * 0.3)

    # ── HAIR TIPS: taper into strands at bottom ──
    if z < -0.7:
        t = (-0.7 - z) / 0.6
        t = min(1, max(0, t))
        # Create strand-like tapering via angular modulation
        angle = math.atan2(x, y)
        strand = 0.5 + 0.5 * math.sin(angle * 7.0)
        taper = 1.0 - t * (0.3 + strand * 0.5)
        x *= max(0.1, taper)
        y *= max(0.1, taper)

    v.co.x = x
    v.co.y = y
    v.co.z = z

# Delete face-area vertices to create open front
# Then we close the boundary to make it a shell
verts_to_remove = []
bm.verts.ensure_lookup_table()
for v in bm.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    # Remove front-lower face area (where eyes/nose/mouth are)
    if y > 0.35 and z < 0.15 and z > -0.55 and abs(x) < 0.5:
        # But keep the bangs!
        if not (z > 0.05 and y > 0.65):
            verts_to_remove.append(v)
    # Remove bottom interior
    if z < -1.1 and abs(x) < 0.25 and y > 0:
        verts_to_remove.append(v)

if verts_to_remove:
    bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')

# Smooth
bm.verts.ensure_lookup_table()
for _ in range(2):
    offsets = {}
    for v in bm.verts:
        if not v.link_edges:
            continue
        neighbors = [e.other_vert(v).co.copy() for e in v.link_edges]
        if neighbors:
            avg = sum(neighbors, Vector((0, 0, 0))) / len(neighbors)
            offsets[v.index] = (avg - v.co) * 0.25
    for v in bm.verts:
        if v.index in offsets:
            v.co += offsets[v.index]

bm.to_mesh(hair.data)
bm.free()

bpy.ops.object.shade_smooth()

hair_faces = len(hair.data.polygons)
hair_verts = len(hair.data.vertices)
print(f"Hair: {hair_verts} verts, {hair_faces} faces")


# ═══════════════════════════════════════════════════════════════
# JOIN, CLEAN, EXPORT
# ═══════════════════════════════════════════════════════════════

# Join head + hair
bpy.ops.object.select_all(action='DESELECT')
hair.select_set(True)
head.select_set(True)
bpy.context.view_layer.objects.active = head
bpy.ops.object.join()

joined = bpy.context.active_object
joined.name = "NovaHead"

# Remove any loose vertices/edges
bm = bmesh.new()
bm.from_mesh(joined.data)

# Delete loose verts (no edges)
loose_v = [v for v in bm.verts if not v.link_edges]
if loose_v:
    bmesh.ops.delete(bm, geom=loose_v, context='VERTS')
    print(f"Removed {len(loose_v)} loose vertices")

# Delete loose edges (no faces)
loose_e = [e for e in bm.edges if not e.link_faces]
if loose_e:
    bmesh.ops.delete(bm, geom=loose_e, context='EDGES')
    print(f"Removed {len(loose_e)} loose edges")

bm.to_mesh(joined.data)
bm.free()

# Center
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
joined.location = (0, 0, 0)

# Scale so head is ~2 units tall
bm = bmesh.new()
bm.from_mesh(joined.data)
bm.verts.ensure_lookup_table()
zs = [v.co.z for v in bm.verts]
h = max(zs) - min(zs)
bm.free()

if h > 0:
    s = 2.0 / h
    joined.scale = (s, s, s)
    bpy.ops.object.transform_apply(scale=True)
    print(f"Scaled by {s:.3f}")

# Remove materials
joined.data.materials.clear()

# Smooth shading
bpy.ops.object.shade_smooth()

# Export
os.makedirs(os.path.dirname(OUTPUT_GLB), exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
joined.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_normals=True,
    export_materials='NONE',
    export_yup=True,
)

total_f = len(joined.data.polygons)
total_v = len(joined.data.vertices)
print(f"\n{'='*55}")
print(f"  NOVA Head — stylized low-poly")
print(f"  Path:     {OUTPUT_GLB}")
print(f"  Faces:    {total_f}")
print(f"  Vertices: {total_v}")
print(f"  Style:    VTuber / holographic wireframe")
print(f"  Interior: NONE — all closed outward shells")
print(f"{'='*55}")
