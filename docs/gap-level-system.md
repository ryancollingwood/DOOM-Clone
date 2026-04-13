# Gap: Level System

## What DOOM Does

DOOM loads all game data from a **WAD** (Where's All the Data) file. A WAD is a flat archive of named **lumps** (data blocks). Levels are defined by a set of lumps: `VERTEXES`, `LINEDEFS`, `SIDEDEFS`, `SECTORS`, `THINGS`, `SEGS`, `SSECTORS`, `NODES`, `REJECT`, `BLOCKMAP`.

The engine loads one level at a time. Special linedef types trigger interactive elements (doors, lifts, crushers, teleporters, exits). Special sector types apply ongoing effects (damage, lighting).

---

## Current State

| Feature | Status |
|---------|--------|
| Hardcoded test level | Implemented (`levels/test_level.py`) |
| Sector geometry with portals | Implemented |
| BSP tree (built at startup) | Implemented |
| WAD file parser | Not implemented |
| Real DOOM map loading | Not implemented |
| THINGS lump (actor spawning) | Not implemented |
| Special linedef actions | Not implemented |
| Special sector types | Not implemented |
| Multiple level sequence | Not implemented |
| Blockmap | Not implemented |
| REJECT table | Not implemented |

---

## Gaps

### G-LVL-01 — WAD File Parser (P1, L)

**What DOOM does**: The WAD format:
```
Header:  4 bytes magic ("IWAD"/"PWAD"), 4 bytes lump count, 4 bytes dir offset
Directory: array of (offset: i32, size: i32, name: 8 char) per lump
Lumps: raw binary data at the offsets
```

**Gap**: A `WADReader` class that:
1. Reads the header and directory.
2. Provides `get_lump(name: str) -> bytes` lookup.
3. Supports both IWAD (full game) and PWAD (patch/mod) with override semantics.

```python
class WADReader:
    def __init__(self, path: str): ...
    def get_lump(self, name: str) -> bytes: ...
    def get_map_lumps(self, map_name: str) -> dict[str, bytes]: ...
    # map_name: "E1M1", "MAP01", etc.
```

**Why important**: Without this, only the hardcoded test level is available. All DOOM content (maps, textures, sprites, sounds) lives in the WAD.

---

### G-LVL-02 — Map Lump Parsing (P1, L)

**What DOOM does**: A DOOM map consists of these lumps (in order after the map marker lump):

#### VERTEXES
Array of `(x: i16, y: i16)` fixed-point coordinates (1 unit = 1/65536 of an arbitrary map unit — in practice, just integers for our purposes).

#### LINEDEFS
Each linedef: `(v1: u16, v2: u16, flags: u16, special: u16, tag: u16, right_sidedef: u16, left_sidedef: u16)`.
- `flags`: bit 0 = impassable, bit 2 = two-sided, bit 3 = upper unpegged, bit 4 = lower unpegged, etc.
- `special`: action type (0 = normal, 1 = door, etc.)
- `tag`: matches sector tag for triggered actions.
- `right_sidedef`/`left_sidedef`: 0xFFFF if absent.

#### SIDEDEFS
Each sidedef: `(x_offset: i16, y_offset: i16, upper_tex: 8 chars, lower_tex: 8 chars, mid_tex: 8 chars, sector: u16)`.

#### SECTORS
Each sector: `(floor_height: i16, ceil_height: i16, floor_flat: 8 chars, ceil_flat: 8 chars, light_level: u16, special: u16, tag: u16)`.

#### THINGS
Each thing: `(x: i16, y: i16, angle: u16, type: u16, flags: u16)`.
- `type`: actor type number (1 = player start, 2 = zombie, 3 = shotgun zombie, etc.)
- `flags`: bit 0 = skill 1–2, bit 1 = skill 3, bit 2 = skill 4–5, bit 3 = deaf.

**Gap**: Parse all five lumps into the existing `Sector`, `Segment` (linedef-based), and a new `Thing` data structure. Map textures by name through a WAD texture loader (see G-LVL-05).

**Implementation notes**:
- Use Python's `struct.unpack_from()` to parse binary lumps.
- Translate DOOM's map coordinate system (Y-up, integer units) to the engine's (Y-up, float).
- Linedefs replace the current `Segment` concept — each linedef that is two-sided generates portal walls; one-sided linedefs generate solid walls. This maps cleanly to the existing `WallModel` types.

---

### G-LVL-03 — Blockmap (P2, M)

**What DOOM does**: The `BLOCKMAP` lump divides the map into a grid of 128×128-unit blocks. Each block contains a list of linedef indices that intersect it. Used for:
- Collision detection (which linedefs could the player be hitting?)
- Line-of-sight (which linedefs to test for occlusion?)
- Monster movement (where can I move without hitting walls?)

**Gap**: Either parse the WAD's BLOCKMAP lump (pre-computed by the map editor) or build one at load time.

**Building at load time** (avoids relying on WAD lump):
```python
class Blockmap:
    def __init__(self, linedefs, origin_x, origin_y, width, height): ...
    def get_linedefs(self, x, y) -> list[int]: ...
    def get_actors_near(self, x, y, radius) -> list[Actor]: ...
```

---

### G-LVL-04 — REJECT Table (P3, M)

**What DOOM does**: The `REJECT` lump is a 2D bit array of `N_sectors × N_sectors` bits. `REJECT[s1][s2] = 1` means sector s1 and sector s2 are confirmed not visible to each other, so monster AI can skip the LOS check.

**Gap**: Parse the REJECT lump and use it as an early-out in `check_sight()` (G-AI-03). Without it the game works but monster AI LOS checks are slower.

---

### G-LVL-05 — WAD Texture & Flat Loading (P1, L)

**What DOOM does**:
- **Wall textures** are defined in `TEXTURE1`/`TEXTURE2` lumps as composites of multiple **patches** (from the `PNAMES` lump).
- **Flat textures** are 64×64 raw 8-bit paletted bitmaps in lumps between `F_START` and `F_END`.
- **Patches** are in the WAD in a post-based column format.
- **Palette** is in `PLAYPAL` (14 palettes of 256×3 bytes). Palette 0 is the normal game palette.
- **Colourmap** is in `COLORMAP` (34 tables of 256 bytes) — used for light diminishing.

**Gap**: A `WADTextureLoader` that:
1. Reads `PLAYPAL` palette.
2. Decodes patch lumps from column format to RGBA bitmaps.
3. Composites `TEXTURE1`/`TEXTURE2` entries into full wall texture bitmaps.
4. Reads flat lumps between `F_START`/`F_END` as 64×64 raw data → RGBA.
5. Uploads all textures to Raylib's GPU with `LoadTextureFromImage()`.

This replaces the current numbered texture files in `/assets/textures/`.

---

### G-LVL-06 — Special Linedef Actions (P1, XL)

**What DOOM does**: 142 unique linedef special types in vanilla DOOM. Key categories:

#### Doors (most common)
| Special | Trigger | Behaviour |
|---------|---------|-----------|
| 1 | Manual Use | DR: door raises, closes after 4s |
| 29 | Manual Use | S1: door raises, stays open |
| 2 | Walk-over | W1: door raises, stays open |
| 46 | Shoot | G1: door raises |
| 117 | Manual Use | DR: blaze door (fast) |

#### Lifts / Platforms
| Special | Trigger | Behaviour |
|---------|---------|-----------|
| 88 | Walk-over | WR: lower lift, wait, raise |
| 62 | Manual Use | SR: lower lift |
| 10 | Walk-over | W1: lower floor to lowest adjacent |

#### Floors / Ceilings
| Special | Behaviour |
|---------|-----------|
| 56 | W1: lower floor, crushing |
| 20 | S1: raise floor to next higher |
| 40 | W1: raise ceiling to highest adjacent |

#### Exits
| Special | Behaviour |
|---------|-----------|
| 11 | S1: exit level (normal) |
| 51 | S1: exit level (secret) |
| 52 | W1: exit level (normal) |

**Gap**: A linedef action system with:
1. Action type registry: `{special_id: ActionHandler}`.
2. Trigger types: `W` (walk-over), `S` (switch), `G` (gun shot), `D` (manual use/door), and whether once (`1`) or repeatable (`R`).
3. **Moving sector** system: sectors can have their floor or ceiling height animated (moving at a fixed speed toward a target height each tic).
4. State tracking: which switches have been activated, which doors are open/closed/moving.

**Moving sector implementation**:
```python
@dataclass
class MovingSector:
    sector_id: int
    target_height: float
    speed: float          # units/tic
    moving_floor: bool    # True = floor, False = ceiling
    direction: int        # +1 = raising, -1 = lowering
    wait_tics: int = 0    # for doors: wait at top before closing
```

Each tic, advance `moving_sector.height` by `speed * direction`, update the sector's floor/ceiling height, re-mesh affected walls.

**Re-meshing** on sector height change is the critical technical challenge: the engine currently pre-builds all wall meshes at load time. Moving sectors require dynamic mesh regeneration for portal walls every tic they are moving. Options:
- Regenerate the affected `WallModel` meshes each tic (straightforward but potentially slow for many moving sectors).
- Use shader-based vertex displacement (complex).
- Pre-build both open and closed mesh states and lerp/swap.

---

### G-LVL-07 — Special Sector Types (P1, L)

**What DOOM does**: Sectors have a `special` field controlling ongoing effects:

| Special | Effect |
|---------|--------|
| 1 | Light flickers randomly |
| 2 | Light strobes fast |
| 3 | Light strobes slow |
| 4 | Light strobes fast + 10/20% damage per tic |
| 5 | 10/20% damage per tic (nukage) |
| 7 | 5% damage per tic |
| 8 | Light oscillates |
| 9 | Secret (counts toward secret %) |
| 10 | Sector closes after 30s (crushing) |
| 11 | 20% damage + end level when player health < 11% |
| 12 | Light strobes slow |
| 13 | Light strobes fast |
| 14 | Door closes after 5 min |
| 16 | 20% damage per tic |
| 17 | Light flickers randomly (alternate) |

**Gap**: A `SectorSpecial` update system run each tic. Damage sectors apply damage to the player when their current sector has a damage special.

---

### G-LVL-08 — Multiple Level Sequence (P1, M)

**What DOOM does**:
- DOOM 1: 3 episodes × 9 levels = 27 levels (E1M1–E3M9).
- Episode select → E1M1 → ... → E1M8 → E1M9 (secret) → E2M1, etc.
- Level exit triggers loading the next map from the WAD.

**Gap**: A `LevelManager` that:
1. Tracks current episode and map number.
2. On exit linedef trigger: saves stats, loads the next level.
3. Maps exit type (normal vs secret) to the correct next level.

```
Episode 1 sequence: E1M1→E1M2→E1M3→E1M4→E1M5→E1M6→E1M7→E1M8→E1M9(secret)
Secret exit from E1M3 → E1M9 → resumes at E1M4
```

---

### G-LVL-09 — Pre-Computed BSP from WAD (P2, M)

**What DOOM does**: The WAD contains pre-built BSP data in `SEGS`, `SSECTORS`, and `NODES` lumps built by the map editor (e.g., DOOM's original `BSP` tool). DOOM loads these directly rather than building them at runtime.

**Current state**: The engine builds a BSP from scratch at startup using `bsp_builder.py`. This works for the test level but will be slow for large DOOM maps with hundreds of linedefs.

**Gap**: Add a WAD BSP lump parser as an alternative to the runtime builder. This is an optimisation rather than a blocker — the runtime builder can be used initially.

---

## Level Loading Pipeline

```
WADReader.get_map_lumps("E1M1")
        ↓
MapParser.parse(lumps)
  ├── parse_vertexes()   → list[Vec2]
  ├── parse_sectors()    → list[Sector]
  ├── parse_sidedefs()   → list[Sidedef]
  ├── parse_linedefs()   → list[Linedef]
  └── parse_things()     → list[Thing]
        ↓
LevelData (current) ← adapt to receive parsed data
        ↓
BSPTreeBuilder (existing) OR WAD BSP lump parser
        ↓
Models (existing wall/flat mesh building)
        ↓
ActorSpawner.spawn_things(things)
  ├── spawn player at Thing type=1
  └── spawn monsters/items at their Thing types
        ↓
Game running
```

---

## Summary Table

| Gap | Priority | Complexity |
|-----|----------|------------|
| G-LVL-01 WAD file parser | P1 | L |
| G-LVL-02 Map lump parsing | P1 | L |
| G-LVL-03 Blockmap | P2 | M |
| G-LVL-04 REJECT table | P3 | M |
| G-LVL-05 WAD texture/flat loading | P1 | L |
| G-LVL-06 Special linedef actions | P1 | XL |
| G-LVL-07 Special sector types | P1 | L |
| G-LVL-08 Multiple level sequence | P1 | M |
| G-LVL-09 Pre-computed BSP from WAD | P2 | M |
