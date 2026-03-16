"""
NOVA Holographic Head Generator — Anime Stylized
Run headless: blender --background --python generate_holo_head_anime.py
Output: holo_head.glb in the same directory as this script

Generates a stylized anime-proportioned female head optimized for
wireframe/holographic rendering in Three.js.

Key anime proportions:
- Large, expressive eyes (1/3 of face height)
- Small, delicate nose and mouth
- Pointed chin, defined jawline
- High cheekbones, smooth forehead
- Slender neck
- Hair volume silhouette
"""

import bpy
import bmesh
import os
import math
from mathutils import Vector

# ─── CONFIGURATION ───────────────────────────────────────────────
OUTPUT_NAME = "holo_head"
TARGET_POLYCOUNT = 3000  # Slightly higher for anime detail + hair
SUBDIVISIONS = 3         # More resolution for delicate features
EXPORT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── CLEAN SCENE ─────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)


def create_head_mesh():
    """Create and sculpt the anime head."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=48,
        ring_count=32,
        radius=1.0,
        location=(0, 0, 0)
    )
    head = bpy.context.active_object
    head.name = "HoloHead"

    # Subdivide for sculpt resolution
    subsurf = head.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = SUBDIVISIONS
    subsurf.render_levels = SUBDIVISIONS
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bm = bmesh.new()
    bm.from_mesh(head.data)
    bm.verts.ensure_lookup_table()

    # ── PRIMARY SCULPT PASS ──────────────────────────────────────
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z

        # ── OVERALL PROPORTIONS ──
        # Anime heads are rounder, slightly wider, taller
        z *= 1.1   # Taller
        x *= 1.02  # Slightly wider
        y *= 0.9   # Shallower front-to-back

        # ── CRANIUM: Smooth, round top ──
        if z > 0.4:
            t = (z - 0.4) / 0.7
            # Keep it round and full on top (anime skulls are very round)
            x *= 1.0 - t * 0.08
            y *= 1.0 - t * 0.05

        # ── FOREHEAD: Smooth, prominent, slightly convex ──
        if z > 0.25 and z < 0.7 and y > 0.4:
            t_z = 1.0 - abs(z - 0.5) / 0.25
            t_x = 1.0 - abs(x) / 0.7
            y += max(0, t_z) * max(0, t_x) * 0.06

        # ── BROW LINE: Subtle, not heavy (anime = soft brows) ──
        if z > 0.15 and z < 0.3 and y > 0.55:
            t = 1.0 - abs(z - 0.22) / 0.07
            t_x = max(0, 1.0 - abs(x) / 0.65)
            y += max(0, t) * t_x * 0.04  # Very subtle

        # ── EYE SOCKETS: Large, wide, anime-proportioned ──
        # Anime eyes are HUGE — roughly 1/3 of face, set wide apart
        for side in [-1, 1]:
            eye_x = 0.32 * side
            eye_z = 0.08       # Slightly lower than realistic
            eye_y_center = 0.65

            dx = (x - eye_x) / 0.20  # Wider horizontally
            dz = (z - eye_z) / 0.14  # Tall vertically
            dy = (y - eye_y_center)

            dist_2d = math.sqrt(dx * dx + dz * dz)
            dist_3d = math.sqrt(dx * dx + dz * dz + dy * dy * 4)

            if dist_3d < 1.5 and y > 0.3:
                # Deep socket with smooth falloff
                falloff = max(0, 1.0 - dist_2d / 1.2)
                falloff = falloff * falloff * falloff  # Cubic for smooth rim
                y -= falloff * 0.14

                # Upper eyelid crease — slight overhang
                if dz > 0.3 and dz < 0.8 and abs(dx) < 0.8:
                    lid_t = 1.0 - abs(dz - 0.55) / 0.25
                    y += max(0, lid_t) * 0.03

                # Lower eye area — gentle curve, not baggy
                if dz < -0.3 and dz > -0.9:
                    lower_t = 1.0 - abs(dz + 0.6) / 0.3
                    # Slight puffiness (anime soft under-eye)
                    y += max(0, lower_t) * max(0, 1.0 - abs(dx) / 0.6) * 0.02

        # ── CHEEKBONES: High, defined but soft ──
        if z > -0.15 and z < 0.1 and y > 0.1:
            t_z = 1.0 - abs(z + 0.02) / 0.12
            t_x = abs(x) / 0.7
            if abs(x) > 0.3:
                push = max(0, t_z) * t_x * 0.1
                x += push * (1 if x > 0 else -1)
                # Soft cheek surface
                y += max(0, t_z) * max(0, 1.0 - abs(abs(x) - 0.55) / 0.2) * 0.03

        # ── CHEEK TAPER: Anime faces narrow quickly below cheekbones ──
        if z > -0.45 and z < -0.1:
            taper_t = (-0.1 - z) / 0.35
            taper_t = max(0, min(1, taper_t))
            x *= 1.0 - taper_t * 0.3

        # ── NOSE: Small, delicate, anime-minimal ──
        # Bridge — very subtle
        if abs(x) < 0.06 and z > -0.05 and z < 0.15 and y > 0.6:
            t_z = 1.0 - abs(z - 0.05) / 0.1
            t_x = 1.0 - abs(x) / 0.06
            y += max(0, t_z) * max(0, t_x) * 0.08

        # Tip — small, slightly upturned
        if abs(x) < 0.08 and z > -0.15 and z < -0.02 and y > 0.6:
            t_z = 1.0 - abs(z + 0.08) / 0.07
            t_x = 1.0 - abs(x) / 0.08
            protrusion = max(0, t_z) * max(0, t_x)
            y += protrusion * 0.12
            # Upturned angle
            z += protrusion * 0.02

        # Nostrils — tiny, barely there
        if abs(x) > 0.02 and abs(x) < 0.07 and z > -0.14 and z < -0.08 and y > 0.6:
            nostril_t = 1.0 - abs(z + 0.11) / 0.03
            x += max(0, nostril_t) * 0.015 * (1 if x > 0 else -1)

        # ── MOUTH AREA: Small, expressive ──
        # Philtrum (upper lip groove)
        if abs(x) < 0.04 and z > -0.25 and z < -0.15 and y > 0.6:
            t = 1.0 - abs(x) / 0.04
            y -= t * 0.015

        # Upper lip — small, defined bow
        if abs(x) < 0.16 and z > -0.3 and z < -0.22 and y > 0.5:
            t_z = 1.0 - abs(z + 0.26) / 0.04
            t_x = 1.0 - abs(x) / 0.16
            y += max(0, t_z) * max(0, t_x) * 0.05
            # Cupid's bow
            if abs(x) < 0.06 and z > -0.26:
                bow_t = 1.0 - abs(x) / 0.06
                z += bow_t * 0.008

        # Lower lip — soft, slightly fuller
        if abs(x) < 0.14 and z > -0.36 and z < -0.28 and y > 0.5:
            t_z = 1.0 - abs(z + 0.32) / 0.04
            t_x = 1.0 - abs(x) / 0.14
            y += max(0, t_z) * max(0, t_x) * 0.04

        # Lip line
        if abs(x) < 0.15 and abs(z + 0.28) < 0.008 and y > 0.6:
            t_x = 1.0 - abs(x) / 0.15
            y -= t_x * 0.012

        # ── CHIN: Pointed, V-shaped (signature anime) ──
        if z < -0.35:
            t = (-0.35 - z) / 0.65
            t = min(1, t)
            # Aggressive V-taper
            x *= 1.0 - t * 0.7
            y *= 1.0 - t * 0.4
            # Chin point protrusion
            if t < 0.25:
                chin_t = 1.0 - t / 0.25
                point_t = max(0, 1.0 - abs(x) / 0.1)
                y += chin_t * point_t * 0.06
                # Slight forward chin
                y += chin_t * 0.02

        # ── JAW: Defined but feminine ──
        if z > -0.45 and z < -0.1 and abs(x) > 0.35:
            t_z = 1.0 - abs(z + 0.25) / 0.2
            jaw_angle = max(0, t_z) * max(0, (abs(x) - 0.35) / 0.25)
            # Clean jaw edge, not bulky
            y -= jaw_angle * 0.04

        # ── TEMPLES: Gentle inward curve ──
        if z > 0.05 and z < 0.4 and abs(x) > 0.55:
            t = (abs(x) - 0.55) / 0.25
            x -= t * 0.04 * (1 if x > 0 else -1)

        # ── EARS: Minimal/hidden (anime often covers with hair) ──
        # Small, flat suggestion of ears
        for side in [-1, 1]:
            ear_x = 0.82 * side
            ear_z = 0.02
            dx = abs(x - ear_x)
            dz = abs(z - ear_z) / 0.15
            dist = math.sqrt(dx * dx + dz * dz)
            if dist < 0.3 and abs(x) > 0.65:
                push = (0.3 - dist) / 0.3
                push = push * push
                x += push * 0.08 * side

        # ── NECK: Slender, feminine ──
        if z < -0.65:
            t = (-0.65 - z) / 0.45
            t = min(1, t)
            # Very slim neck
            neck_scale = 0.42 - t * 0.03
            x *= neck_scale
            y *= neck_scale * 0.9  # Slightly oval
            # Subtle forward lean
            y += t * 0.04

        # ── BACK OF HEAD: Round, full ──
        if y < -0.4 and z > -0.3 and z < 0.5:
            t_y = (-0.4 - y) / 0.4
            t_z = 1.0 - abs(z - 0.1) / 0.4
            y -= max(0, t_y) * max(0, t_z) * 0.08

        v.co.x = x
        v.co.y = y
        v.co.z = z

    # Smooth to blend
    smooth_mesh(bm, iterations=5, factor=0.3)

    # ── SHARPENING PASS ──────────────────────────────────────────
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z

        # Re-sharpen nose tip
        if abs(x) < 0.06 and z > -0.12 and z < -0.02 and y > 0.6:
            t = (1.0 - abs(x) / 0.06) * (1.0 - abs(z + 0.07) / 0.05)
            y += max(0, t) * 0.04

        # Re-define eye sockets
        for side in [-1, 1]:
            dx = (x - 0.32 * side) / 0.18
            dz = (z - 0.08) / 0.12
            dist = math.sqrt(dx * dx + dz * dz)
            if dist < 1.0 and y > 0.4:
                indent = (1.0 - dist)
                indent = indent * indent
                y -= indent * 0.04

        # Re-define chin point
        if z < -0.5 and abs(x) < 0.08:
            t = max(0, (-0.5 - z) / 0.3)
            y += (1.0 - abs(x) / 0.08) * t * 0.02

        # Re-define jawline
        if z > -0.5 and z < -0.2 and abs(x) > 0.3 and abs(x) < 0.55:
            t_z = 1.0 - abs(z + 0.35) / 0.15
            t_x = 1.0 - abs(abs(x) - 0.42) / 0.12
            if max(0, t_z) * max(0, t_x) > 0.3:
                y -= 0.015

        v.co.x = x
        v.co.y = y
        v.co.z = z

    # Light final smooth
    smooth_mesh(bm, iterations=2, factor=0.15)

    bm.to_mesh(head.data)
    bm.free()
    head.data.update()

    return head


def create_hair_volume():
    """
    Create stylized anime hair as a separate mesh.
    Adds volume and silhouette — the wireframe shader makes it look digital.
    """
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=24,
        radius=1.0,
        location=(0, 0, 0)
    )
    hair = bpy.context.active_object
    hair.name = "HoloHair"

    # Subdivide
    subsurf = hair.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bm = bmesh.new()
    bm.from_mesh(hair.data)
    bm.verts.ensure_lookup_table()

    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z

        # Scale to be slightly larger than head
        x *= 1.12
        y *= 1.05
        z *= 1.15

        # ── HAIR VOLUME: Bigger on top and sides ──
        if z > 0.2:
            t = (z - 0.2) / 0.8
            # Poofy top
            x *= 1.0 + t * 0.15
            y *= 1.0 + t * 0.1
            z *= 1.0 + t * 0.08

        # ── SIDE HAIR: Frames face, flows down ──
        if abs(x) > 0.4 and z < 0.2:
            # Hair drapes down the sides
            side_t = (0.2 - z) / 1.2
            side_t = max(0, min(1, side_t))
            # Keep width, extend downward
            if z < -0.3:
                x *= 1.0 + side_t * 0.05

        # ── BACK HAIR: Longer, flowing ──
        if y < -0.2:
            back_t = (-0.2 - y) / 0.6
            back_t = max(0, min(1, back_t))
            # Extends lower in back
            if z < -0.2:
                z_offset = back_t * 0.2
                z -= z_offset

        # ── FRONT BANGS: Cover forehead partially ──
        if y > 0.5 and z > 0.2 and z < 0.65:
            bang_t = 1.0 - abs(z - 0.4) / 0.25
            bang_t = max(0, bang_t)
            # Push bangs forward
            y += bang_t * 0.15
            # Taper bangs into strands at the bottom
            if z < 0.35:
                strand = math.sin(x * 12) * 0.02
                y += strand
                x += strand * 0.5

        # ── REMOVE INTERIOR (face opening) ──
        # Don't render hair where the face should show through
        # We'll handle this by removing faces later

        # ── HAIR TIPS: Taper to points ──
        if z < -0.6:
            t = (-0.6 - z) / 0.5
            t = min(1, t)
            # Create strand-like tapering
            strand_freq = 8
            strand_phase = math.atan2(x, y) * strand_freq
            strand_mod = 0.5 + 0.5 * math.sin(strand_phase)
            taper = 1.0 - t * (0.3 + strand_mod * 0.4)
            x *= max(0.1, taper)
            y *= max(0.1, taper)

        v.co.x = x
        v.co.y = y
        v.co.z = z

    # Remove face-area vertices (front of hair below forehead)
    verts_to_remove = []
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        # Remove the front-facing lower portion that would cover the face
        if y > 0.3 and z < 0.3 and z > -0.5 and abs(x) < 0.5:
            # But keep the bangs
            if not (z > 0.15 and y > 0.6):
                verts_to_remove.append(v)
        # Remove bottom interior
        if z < -0.8 and abs(x) < 0.3 and y > 0:
            verts_to_remove.append(v)

    if verts_to_remove:
        bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')

    smooth_mesh(bm, iterations=3, factor=0.3)

    bm.to_mesh(hair.data)
    bm.free()
    hair.data.update()

    return hair


def smooth_mesh(bm, iterations=2, factor=0.5):
    """Laplacian-like smoothing."""
    bm.verts.ensure_lookup_table()
    for _ in range(iterations):
        offsets = {}
        for v in bm.verts:
            if not v.link_edges:
                continue
            neighbors = [e.other_vert(v).co.copy() for e in v.link_edges]
            if neighbors:
                avg = sum(neighbors, Vector((0, 0, 0))) / len(neighbors)
                offsets[v.index] = (avg - v.co) * factor
        for v in bm.verts:
            if v.index in offsets:
                v.co += offsets[v.index]


# ─── BUILD ───────────────────────────────────────────────────────
head = create_head_mesh()
hair = create_hair_volume()

# ─── JOIN MESHES ─────────────────────────────────────────────────
# Select both objects
bpy.ops.object.select_all(action='DESELECT')
hair.select_set(True)
head.select_set(True)
bpy.context.view_layer.objects.active = head
bpy.ops.object.join()

joined = bpy.context.active_object
joined.name = "HoloHead"

# ─── DECIMATE ────────────────────────────────────────────────────
current_polys = len(joined.data.polygons)
if current_polys > TARGET_POLYCOUNT:
    ratio = TARGET_POLYCOUNT / current_polys
    decimate = joined.modifiers.new(name="Decimate", type='DECIMATE')
    decimate.ratio = ratio
    decimate.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier="Decimate")

# ─── CLEAN UP ────────────────────────────────────────────────────
# Remove loose vertices
bm = bmesh.new()
bm.from_mesh(joined.data)

# Remove anything below the neck cutoff
verts_to_remove = [v for v in bm.verts if v.co.z < -1.15]
if verts_to_remove:
    bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')

# Remove loose/disconnected verts
loose = [v for v in bm.verts if not v.link_edges]
if loose:
    bmesh.ops.delete(bm, geom=loose, context='VERTS')

bm.to_mesh(joined.data)
bm.free()

# ─── SMOOTH NORMALS ──────────────────────────────────────────────
bpy.ops.object.shade_smooth()

# ─── CENTER ──────────────────────────────────────────────────────
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
joined.location = (0, 0, 0)

# ─── EXPORT ──────────────────────────────────────────────────────
output_path = os.path.join(EXPORT_DIR, f"{OUTPUT_NAME}.glb")

# Select only our head for export
bpy.ops.object.select_all(action='DESELECT')
joined.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_normals=True,
    export_vertex_color='NONE',
    export_materials='NONE',
    export_yup=True,
)

final_polys = len(joined.data.polygons)
print(f"\n{'='*55}")
print(f"  NOVA Holographic Head (Anime) exported")
print(f"  Path:     {output_path}")
print(f"  Polygons: {final_polys}")
print(f"  Style:    Anime / Stylized Female")
print(f"  Format:   GLB (no materials — shader-driven)")
print(f"{'='*55}\n")
