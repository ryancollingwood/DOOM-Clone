# Gap: Player Physics

## What DOOM Does

DOOM's player physics are 2D in nature — the engine uses a fixed-point 2D map for movement and collision, then maps the Z axis (height) to the current sector's floor. Key behaviours:

### Movement
- **Speed**: Walk = 25 map units/tic (35 tics/sec ≈ 875 mu/s), Run = 50 mu/tic when Shift held
- **Turning**: 2.8125° per tic (keyboard); mouse look is horizontal-only in vanilla
- **Momentum**: `momentum` vector decays by factor of ~0.7906 each tic (friction)
- **Diagonal movement**: full speed in both axes simultaneously (no correction in vanilla)
- **No vertical freelook**: vanilla DOOM uses a pitch-zero camera; looking up/down is a stretch hack
- **No jumping**: the player cannot jump voluntarily

### Collision Detection
- Player is modelled as a **circle** of radius 16 map units
- Collision against linedefs using a "box vs segment" sweep
- **Sliding**: when blocked, player slides along the wall (velocity projected onto wall normal)
- **Step-up**: automatically steps up floor height differences ≤ 24 units
- **Ceiling block**: player cannot enter a sector where `ceiling - floor < 56` units (player height = 56)

### Gravity & Vertical Movement
- When player's Z > floor Z: fall at accelerating rate (DOOM gravity = 1 mu/tic²)
- No air control — horizontal movement continues unchanged during fall
- Landing does not cause damage (DOOM 1 has no fall damage)
- Sector floor is authoritative: player Z is always ≥ sector floor Z

### Sector Interaction
- **Current sector**: determined by point-in-sector test each tic
- **Floor height**: player Z snaps to `sector.floor_height` when standing
- **Damage sectors**: special sector types deal periodic damage
- **Push sectors** (boom extension): not in vanilla

### Use Action
- Press `E` (or spacebar in vanilla) to activate linedefs within 64 units in front of player
- Searches through linedefs in the player's facing BLOCKMAP column
- Triggers doors, lifts, switches, exits

---

## What We Have

| Feature | Status |
|---------|--------|
| First-person camera | Implemented (`camera.py`) |
| WASD movement + strafing | Implemented (`input_handler.py`) |
| Mouse-look yaw/pitch | Implemented (full 6DOF) |
| Wall collision | **Not implemented** — player clips through walls |
| Floor/ceiling collision | **Not implemented** — player floats freely |
| Sector floor tracking | **Not implemented** — player height is free |
| Step-up | **Not implemented** |
| Gravity | **Not implemented** |
| Momentum / friction | **Not implemented** |
| Use action | **Not implemented** |
| Player death | **Not implemented** |

The camera is effectively a free-flying observer with no physical presence in the world. Movement speed and diagonal correction differ from DOOM convention.

---

## Gaps

### G-PP-01 — Wall Collision Detection (P1, M)

**Need**: Treat player as a circle of radius ~16 units. Each movement step, check the candidate position against all linedefs in the player's BLOCKMAP cells. If blocked, project velocity onto the wall to slide.

**Approach**:
- Implement a `Blockmap` structure: divide map into a 128×128-unit grid, each cell holds a list of linedef indices that pass through it.
- For each movement: collect linedefs in nearby cells, test circle–segment overlap, compute slide vector.
- Use the same linedef list as the existing `level_data` segment data; linedefs are 1:1 with segments for solid walls.

**Edge cases**: Corners (two-wall collision), portal linedefs that should not block movement at the step height boundary.

---

### G-PP-02 — Sector Floor Tracking (P1, S)

**Need**: Determine which sector the player's XZ position (DOOM XY) is in, then set `player.z = sector.floor_height`.

**Approach**:
- Point-in-polygon test against each sector's outline. The BSP tree can accelerate this: traverse to the leaf node containing the point.
- Already have `BSPTreeTraverser`; add a `sector_at(x, z)` query that walks the tree and returns the sector.
- Set camera Y to `sector.floor_height + EYE_HEIGHT` each tic.

---

### G-PP-03 — Step-Up (P1, S)

**Need**: When the destination sector floor is higher by ≤ 24 units, automatically elevate the player.

**Approach**:
- After resolving XZ movement, compare destination sector floor height to current floor height.
- If `delta ≤ 24`: move the player up. If `delta > 24`: block movement (treat as wall).
- Requires G-PP-02 to be implemented first.

---

### G-PP-04 — Ceiling Collision (P1, S)

**Need**: Player cannot move into a sector where `ceiling_height - floor_height < PLAYER_HEIGHT` (56 units).

**Approach**:
- During sector lookup (G-PP-02), check if headroom ≥ PLAYER_HEIGHT. If not, block entry.

---

### G-PP-05 — Gravity & Falling (P1, S)

**Need**: When player Z > current sector floor Z (e.g., walked off a ledge), apply downward acceleration until landing.

**Approach**:
- Track `player.vz` (vertical velocity).
- Each tic: if `player.z > floor_z`: `player.vz -= GRAVITY` (DOOM uses 1 mu/tic²).
- Clamp `player.z = floor_z` on landing, reset `player.vz = 0`.
- No fall damage needed for DOOM 1 parity.

---

### G-PP-06 — Momentum & Friction (P2, S)

**Need**: DOOM movement is momentum-based with friction, not instantaneous velocity.

**Approach**:
- Replace direct position update with velocity accumulation:
  - `velocity += input_direction * ACCEL`
  - `velocity *= FRICTION` (≈ 0.7906 per tic when on ground)
  - `position += velocity`
- This gives the classic DOOM "sliding" feel when stopping.

---

### G-PP-07 — Use Action (P1, M)

**Need**: Player presses E (or spacebar) to interact with linedefs within 64 units in the facing direction.

**Approach**:
- Compute a short ray from player position in facing direction (length = 64 units).
- Find all linedefs the ray intersects (using the blockmap).
- If a linedef has a special type, trigger its action (door open, switch flip, etc.).
- Requires the linedef special system from the level loading gap.

---

### G-PP-08 — No Vertical Freelook (P4, S)

**Current state**: The camera has full ±89° pitch from mouse look.

**DOOM behaviour**: Vanilla has no pitch at all. Source ports added optional Y-axis look. This is a tuning/toggle decision, not blocking.

**Approach**:
- Add a `VANILLA_LOOK` config flag in `settings.py`. When enabled, ignore mouse Y delta and lock pitch to 0.
- Current implementation can stay as the "extended" mode.

---

## Implementation Dependencies

```
WAD/Level loading (sector data with heights)
        ↓
G-PP-02  Sector floor tracking
        ↓
G-PP-01  Wall collision  ←→  Blockmap
G-PP-03  Step-up
G-PP-04  Ceiling collision
G-PP-05  Gravity
        ↓
G-PP-06  Momentum / friction
G-PP-07  Use action
```

---

## Complexity Estimates

| Gap | Estimate |
|-----|----------|
| G-PP-01 Wall collision | M |
| G-PP-02 Sector floor tracking | S |
| G-PP-03 Step-up | S |
| G-PP-04 Ceiling collision | S |
| G-PP-05 Gravity | S |
| G-PP-06 Momentum / friction | S |
| G-PP-07 Use action | M (depends on linedef specials) |
| G-PP-08 No vertical freelook | S |
