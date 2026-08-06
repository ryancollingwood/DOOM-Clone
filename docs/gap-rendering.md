# Gap: Rendering

## What DOOM Does

DOOM's renderer is a software column-based renderer that works entirely in 2D screen space. This clone uses Raylib/OpenGL with 3D meshes — a valid alternative approach — but several DOOM-specific visual systems are still missing.

---

## Current State

| Feature | Status |
|---------|--------|
| BSP-based static geometry | Implemented |
| Textured walls | Implemented |
| Textured floors/ceilings | Implemented |
| Multi-height portals | Implemented |
| Dynamic wall shading (single light) | Implemented (approximate) |
| Sprite rendering | Not implemented |
| Per-sector light levels | Not implemented |
| Distance-based light diminishing | Not implemented |
| Sky rendering | Not implemented |
| Wall texture offsets | Not implemented |
| Animated textures | Not implemented |
| Automap (full) | Partial (minimap overlay only) |
| Weapon overlay sprites | Not implemented |
| Screen transitions | Not implemented |
| Fuzz/spectre effect | Not implemented |

---

## Gaps

### G-REN-01 — Per-Sector Lighting (P2, S)

**What DOOM does**: Each sector has a `light_level` 0–255. This directly scales the colour of all surfaces in that sector (walls, floors, ceilings). Bright sectors (255) are fully lit; dark sectors (0) are pitch black.

**Current state**: A single `LIGHT_POS` vec2 in `settings.py` determines shading via dot product against wall normals. There is no per-sector brightness; all sectors share the same lighting model.

**Gap**: Sectors in `level_data.py` / `data_types.py` have no `light_level` field. The `Sector` dataclass needs this field, and both `WallModel` and `FlatModel` must apply it as a tint multiplier.

**Implementation notes**:
- Add `light_level: int = 160` to the `Sector` dataclass (`data_types.py`).
- In `WallModel.get_shading()` and `FlatModel`, compute `tint = light_level / 255.0`.
- Multiply the existing directional shading result by `tint`.
- In `test_level.py` and eventually WAD loading, populate `light_level` from SECTORS lump.

---

### G-REN-02 — Distance-Based Light Diminishing / Colourmap (P2, M)

**What DOOM does**: Light diminishes with distance from the player. At a given sector `light_level`, surfaces farther away become progressively darker. DOOM uses a precomputed `COLORMAP` lump with 34 shade levels, choosing a shade based on distance and `light_level`.

**Current state**: No distance-based attenuation. Lighting is purely directional.

**Gap**: Need to compute screen-space (or world-space) distance for each wall/flat surface and apply a darkness multiplier.

**Implementation notes**:
- Compute the distance from the camera to the midpoint of each wall segment.
- Map distance → shade index: `shade = clamp(distance / SHADE_DISTANCE, 0, 1)`.
- Blend wall colour with black based on shade index and sector `light_level`.
- In Raylib/OpenGL this can be approximated with a fog effect or a per-vertex colour lerp toward black. True DOOM COLORMAP fidelity requires per-column software rendering.
- Raylib's `BeginMode3D` supports fog: `SetFogParams()` can approximate this cheaply.

---

### G-REN-03 — Sprite Billboarding System (P1, L)

**What DOOM does**: All dynamic objects (monsters, items, decorations, projectiles) are 2D sprites that always face the camera. Sprite frames are chosen based on the angle between the camera direction and the actor's facing angle (8-direction sprites for monsters).

**Current state**: No sprite rendering exists. The engine renders only static level geometry.

**Gap**: This is the largest single rendering gap. Without sprites, enemies, items, and weapons are invisible.

**Implementation notes**:
- Sprites must be drawn as billboards: quads that rotate around the Y axis to face the camera.
- In 3D renderer terms: compute the vector from sprite to camera, use it as the quad's facing vector.
- Raylib has `DrawBillboard()` and `DrawBillboardRec()` for this purpose.
- Sprite sheets: DOOM sprites are stored per-actor as named patches in the WAD (e.g., `POSSA1`, `POSSB1`...). Each name encodes actor name (4 chars), frame letter, and rotation angle.
- 8 rotations per frame allow the closest-matching angle to be shown.
- Sprites must be depth-sorted against level geometry (drawn after opaque walls, before UI).
- **Clipping**: in the software renderer, sprites are clipped to the column ranges drawn by walls. In an OpenGL approach, depth testing handles this naturally.
- Alpha testing needed for transparent pixels in sprite patches.

**Sub-tasks**:
1. Sprite patch loader (WAD PATCH format → texture)
2. Actor position → billboard quad
3. Angle-to-rotation-frame selection
4. Depth-sorted draw call order
5. Alpha-test material for sprites

---

### G-REN-04 — Wall Texture Offsets (P2, S)

**What DOOM does**: Each sidedef has `x_offset` and `y_offset` values that shift the texture horizontally and vertically. This is used to align textures at corners, doors, etc.

**Current state**: `WallModel` computes UV coordinates from geometry but ignores any per-wall texture offsets. The `Segment` dataclass has no offset fields.

**Gap**: Add `x_offset` and `y_offset` to `Segment` (or sidedef data), pass them into `WallModel.get_quad_mesh()` as UV shifts.

**Implementation notes**:
- In `WallModel.get_quad_mesh()`, add `u_offset` and `v_offset` to all UV coordinates.
- Offsets come from the SIDEDEFS lump when loading WAD maps.
- For the current test level, offsets can default to (0, 0).

---

### G-REN-05 — Animated Wall Textures (P3, M)

**What DOOM does**: Certain wall textures are part of animation sequences defined in the engine (hardcoded in vanilla; in ANIMDEFS in modern ports). For example: `BLODGR1`→`BLODGR2`→`BLODGR3`→`BLODGR4` cycles at 8 tics/frame.

**Current state**: Textures are loaded once at startup and never change. No animation system exists.

**Gap**: Need a texture animation manager that advances through frame sequences each tic and updates the GPU texture or swaps the Raylib `Texture2D` reference.

**Implementation notes**:
- Define animation sequences: `[(tex_id_start, tex_id_end, tics_per_frame), ...]`
- In the update loop, increment a per-sequence timer; when it hits `tics_per_frame`, advance the frame index.
- Either swap `Texture2D` references in the wall models, or use a texture array with a frame-index uniform.

---

### G-REN-06 — Animated Flat Textures (P3, M)

Same as G-REN-05 but for floor/ceiling flats. Key vanilla sequences include nukage (`NUKAGE1–3`), water (`FWATER1–4`), and lava (`LAVA1–4`).

---

### G-REN-07 — Sky Rendering (P2, M)

**What DOOM does**: The `F_SKY1` flat used on a ceiling sector triggers sky rendering instead of a texture. The sky is a texture (`SKY1`, `SKY2`, `SKY3` per episode) that scrolls horizontally based on player yaw angle.

**Current state**: All ceilings render their assigned flat texture. No sky handling exists.

**Gap**: Detect `F_SKY1` ceiling sectors during rendering and render a sky quad instead.

**Implementation notes**:
- Sky can be implemented as a large hemisphere or a full-screen background texture.
- Simpler approach: render sky as an infinitely tall backdrop that fills ceiling pixels.
- In Raylib/OpenGL: draw a sky quad at far clip plane, or use a skybox.
- The sky texture should scroll based on player yaw: `u_offset = player.yaw / (2 * pi)`.
- For wall upper textures bordering sky ceilings, DOOM leaves them undrawn (transparent to sky). In our renderer, simply skip upper portal walls when the back sector ceiling uses `F_SKY1`.

---

### G-REN-08 — Full Automap (P3, M)

**What DOOM does**: The automap shows:
- All revealed linedefs (only those the player has walked near)
- Colour coding: one-sided walls (red/white), two-sided walkable (yellow), two-sided impassable, secret (purple/grey)
- Player position with triangle indicator and direction arrow
- Automap panning and zoom
- Optional "all map" view (IDDT cheat)
- Marks (M key to place markers on map)

**Current state**: A minimap overlay exists (`map_renderer.py`) that shows all segments, BSP splits, and camera position. It is not reveal-based and lacks DOOM's colour conventions.

**Gap**:
- Track which linedefs are "revealed" (player has been within ~1024 units).
- Apply DOOM colour conventions to linedef types.
- Add automap pan/zoom controls (arrow keys in DOOM).
- Implement automap as a full-screen toggle, not a minimap overlay.

---

### G-REN-09 — Weapon Sprite Overlay (P1, M)

**What DOOM does**: The currently held weapon is rendered as a 2D sprite in the centre-bottom of the screen, in front of all 3D geometry. Weapon sprites include idle bob, raise/lower animations, and firing frames.

**Current state**: No foreground 2D sprite layer exists.

**Gap**: Need a 2D overlay rendering pass after the 3D scene that draws the weapon sprite at fixed screen coordinates. Weapon bob applies a sinusoidal vertical offset based on player movement speed.

**Implementation notes**:
- Raylib: after `EndMode3D()`, draw weapon sprites using `DrawTextureRec()` in screen space.
- Weapon bob: `y_offset = sin(time * BOB_FREQ) * BOB_AMP * move_speed / MAX_SPEED`.
- Weapon sprites are larger than actor sprites and centred slightly below screen middle.
- Firing animation cycles through frames at a fixed tic rate.

---

### G-REN-10 — Fuzz / Spectre Effect (P4, M)

**What DOOM does**: The Spectre (invisible Demon) uses a "fuzz" shader that samples from a distorted pixel offset table, making the sprite appear as a corrupted static region.

**Current state**: Not implemented.

**Gap**: In a 3D renderer, this can be approximated with a screen-space distortion shader or a partial transparency effect using a noise mask.

---

### G-REN-11 — Screen Wipe Transition (P4, M)

**What DOOM does**: Between level loads, a "melt" transition plays where the new screen appears to melt downward over the old one.

**Current state**: No transitions.

**Gap**: Capture old framebuffer, render new scene, apply column-by-column downward reveal animation.

---

## Summary Table

| Gap | Priority | Complexity |
|-----|----------|------------|
| G-REN-01 Per-sector lighting | P2 | S |
| G-REN-02 Distance diminishing | P2 | M |
| G-REN-03 Sprite billboarding | P1 | L |
| G-REN-04 Wall texture offsets | P2 | S |
| G-REN-05 Animated wall textures | P3 | M |
| G-REN-06 Animated flat textures | P3 | M |
| G-REN-07 Sky rendering | P2 | M |
| G-REN-08 Full automap | P3 | M |
| G-REN-09 Weapon sprite overlay | P1 | M |
| G-REN-10 Fuzz/spectre effect | P4 | M |
| G-REN-11 Screen wipe transition | P4 | M |
