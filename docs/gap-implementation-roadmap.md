# Implementation Roadmap

Phased plan to achieve gameplay parity with the original DOOM (1994). Phases are ordered by dependency and player-visible impact. Each phase produces a testable milestone.

---

## Dependency Graph (High Level)

```
Phase 1: Foundation
  WAD Parser ──────────────────────────────────────────┐
  Map Lump Parsing ────────────────────────────────────┤
  Game State Manager ──────────────────────────────────┤
                                                        ▼
Phase 2: Playable World                         Level loads from WAD
  Player Physics (collision, gravity, sectors) ────────┐
  Blockmap ────────────────────────────────────────────┤
  Per-sector lighting ─────────────────────────────────┤
                                                        ▼
Phase 3: Player                              Player stands in world
  Health / Armour / Ammo ────────────────────────────┐
  Weapon system (fire, hitscan, projectiles) ─────────┤
  Status bar HUD ──────────────────────────────────────┤
  Menus (main, skill, pause) ──────────────────────────┤
                                                        ▼
Phase 4: Enemies                              Player can fight
  Actor system + state machine ──────────────────────┐
  Sprite renderer ─────────────────────────────────────┤
  Thing spawning ──────────────────────────────────────┤
  Monster AI (sight, chase, attack) ──────────────────┤
  Item pickup ─────────────────────────────────────────┤
                                                        ▼
Phase 5: Interactivity                       Enemies fight back
  Special linedefs (doors, lifts, exits) ────────────┐
  Special sector types ───────────────────────────────┤
  Keys & locked doors ────────────────────────────────┤
  Level sequence (next map on exit) ─────────────────┤
  Teleporters ────────────────────────────────────────┤
                                                        ▼
Phase 6: Audio                               Levels are completable
  Sound effects ─────────────────────────────────────┐
  Positional audio ───────────────────────────────────┤
  Music playback ─────────────────────────────────────┤
                                                        ▼
Phase 7: Polish                             Core game loop complete
  WAD texture/flat loading ──────────────────────────┐
  Animated textures & flats ──────────────────────────┤
  Sky rendering ──────────────────────────────────────┤
  Distance light diminishing ──────────────────────────┤
  Intermission screen ─────────────────────────────────┤
  Automap (full) ──────────────────────────────────────┤
  Difficulty scaling ──────────────────────────────────┤
  Power-ups ──────────────────────────────────────────┤
  Save / Load ─────────────────────────────────────────┤
                                                        ▼
                                              Feature-complete
```

---

## Phase 1 — Foundation

**Goal**: Load a real DOOM map into the existing renderer.

**Milestone**: E1M1 renders correctly (geometry only, no actors, no physics).

| Task | Gap Ref | Complexity | Notes |
|------|---------|------------|-------|
| WAD file parser | G-LVL-01 | L | Binary reader, directory lookup |
| Map lump parsing (VERTEXES, LINEDEFS, SIDEDEFS, SECTORS) | G-LVL-02 | L | Adapt output to `LevelData` |
| WAD flat texture loading | G-LVL-05 (flats) | M | 64×64 paletted → Raylib texture |
| WAD wall texture loading | G-LVL-05 (walls) | L | Patch composite system |
| Game state manager | G-GS-01 | S | GameState enum + dispatcher |
| Wall texture offsets | G-REN-04 | S | UV shifts from sidedef data |
| Per-sector lighting | G-REN-01 | S | `light_level` tint on render |

**Estimated effort**: 4–6 weeks

---

## Phase 2 — Playable World

**Goal**: Player can walk around a DOOM map without clipping through walls.

**Milestone**: Walk around E1M1, doors remain closed, no enemies.

| Task | Gap Ref | Complexity | Notes |
|------|---------|------------|-------|
| Blockmap (at load time) | G-LVL-03 | M | Grid spatial index of linedefs |
| Wall collision detection | G-PP-01 | M | Circle vs linedef with slide |
| Sector floor tracking | G-PP-02 | S | BSP point-in-sector query |
| Step-up | G-PP-03 | S | Auto-elevate ≤ 24 units |
| Ceiling collision | G-PP-04 | S | Block entry to low-headroom sectors |
| Gravity / falling | G-PP-05 | S | Fall off ledges |
| Momentum & friction | G-PP-06 | S | DOOM movement feel |
| Use action (no-op for now) | G-PP-07 (partial) | S | Ray cast, no triggers yet |

**Estimated effort**: 2–3 weeks

---

## Phase 3 — Player Systems

**Goal**: Player has health/ammo/weapons, can shoot, has a working HUD and menus.

**Milestone**: Player can fire a pistol and die.

| Task | Gap Ref | Complexity | Notes |
|------|---------|------------|-------|
| PlayerState (health, armour, ammo) | G-CMB-01, G-CMB-02 | S | Dataclass |
| DOOM RNG | G-CMB-07 | S | Fixed table for reproducibility |
| Weapon slot system | G-CMB-03 | L | State machine, sprite frames |
| Hitscan attack | G-CMB-04 | M | Ray vs linedefs + actors |
| Melee attack | G-CMB-06 | S | Short-range hitscan |
| Player death | G-CMB-09 | S | Lock input, tilt view |
| Status bar | G-HUD-01 | M | Health, ammo, armour |
| HUD messages | G-HUD-02 | S | Timed text overlay |
| Main menu | G-HUD-03 | M | Stack-based navigation |
| Episode / skill select | G-HUD-04 | S | Sub-menus |
| Pause (ESC) | G-HUD-05 | S | Freeze tic updates |
| Weapon overlay sprite | G-REN-09 | M | 2D foreground layer |

**Estimated effort**: 3–4 weeks

---

## Phase 4 — Enemies

**Goal**: Monsters are visible, alert, chase, and attack the player.

**Milestone**: Kill an Imp in E1M1.

| Task | Gap Ref | Complexity | Notes |
|------|---------|------------|-------|
| Actor base class | G-AI-01 | L | mobj_t equivalent |
| State machine | G-AI-02 | L | States, tics, action fns |
| Thing spawning | G-GS-02 | M | Place actors from THINGS lump |
| Sprite billboard renderer | G-REN-03 | L | DrawBillboard + angle selection |
| Sprite patch loader (WAD) | G-REN-03 sub | M | Column-format decoder |
| Line-of-sight check | G-AI-03 | M | 2D ray vs BSP |
| Monster alert | G-AI-04 | S | Flood-fill noise propagation |
| Chase / pathfinding | G-AI-05 | M | A_Chase implementation |
| Monster attacks | G-AI-06 | M | Per-monster attack functions |
| Projectile actors | G-CMB-05 | M | Moving missile actors |
| Monster pain & death | G-AI-07 | M | Pain chance, death state, corpse |
| Damage randomisation | G-CMB-07 | S | Use DoomRNG |
| Item pickup | G-GS-03 | M | Touch detection + effects |
| Splash damage | G-CMB-08 | S | Radius damage from rockets |

**Estimated effort**: 5–7 weeks

---

## Phase 5 — Interactivity

**Goal**: Doors open, lifts move, levels can be completed.

**Milestone**: Complete E1M1 through the exit and load E1M2.

| Task | Gap Ref | Complexity | Notes |
|------|---------|------------|-------|
| Moving sector system | G-LVL-06 (core) | L | Floors/ceilings animated per tic |
| Door linedef actions | G-LVL-06 | M | Types 1, 29, 117, etc. |
| Lift linedef actions | G-LVL-06 | M | Types 10, 62, 88, etc. |
| Exit linedef actions | G-LVL-06 | S | Types 11, 52 |
| Special sector types | G-LVL-07 | L | Damage, lights, secret areas |
| Use action (full) | G-PP-07 | M | Trigger linedefs on E press |
| Key system | G-GS-04 | S | Carry keys, check on doors |
| Key-locked doors | G-LVL-06 sub | S | Require key check |
| Level sequence | G-LVL-08 | M | Load next map on exit |
| Intermission screen | G-HUD-06 | M | Stats display |
| Teleporters | G-GS-08 | M | Linedef special + landing Thing |
| Kill/item/secret tracking | G-GS-07 | S | Counters + percentage |

**Estimated effort**: 4–5 weeks

---

## Phase 6 — Audio

**Goal**: Full audio: sounds and music.

**Milestone**: Hear gunfire, monster growls, and music.

| Task | Gap Ref | Complexity | Notes |
|------|---------|------------|-------|
| Audio device init (Raylib) | G-AUD-01 | S | `ray.init_audio_device()` |
| Sound effect playback | G-AUD-01 | M | Load + play per event |
| Sound priority system | G-AUD-04 | S | Channel management |
| Distance attenuation | G-AUD-05 | S | Volume falloff |
| Positional panning | G-AUD-02 | M | Left/right per actor angle |
| Music playback (OGG) | G-AUD-03 | M | Per-level track streaming |
| Player sound feedback | G-AUD-06 | S | Pain, death, pickup sounds |

**Estimated effort**: 2–3 weeks

---

## Phase 7 — Polish

**Goal**: Full feature parity with DOOM (1994).

**Milestone**: All episodes completable with authentic DOOM experience.

| Task | Gap Ref | Complexity | Notes |
|------|---------|------------|-------|
| Distance light diminishing | G-REN-02 | M | Fog / colourmap effect |
| Animated wall textures | G-REN-05 | M | Sequence timer system |
| Animated flat textures | G-REN-06 | M | Same system for flats |
| Sky rendering | G-REN-07 | M | F_SKY1 ceiling → sky texture |
| Full automap | G-REN-08 | M | Reveal-based, DOOM colour coding |
| Monster infighting | G-AI-08 | M | Retarget on friendly-fire |
| All 9 monsters (data) | G-AI-09 | XL | State tables + stats |
| Difficulty scaling | G-GS-06 | M | Thing filters + damage multiplier |
| Power-ups | G-GS-05 | M | Timed effect system |
| REJECT table | G-LVL-04 | M | LOS early-out optimisation |
| Fuzz/spectre effect | G-REN-10 | M | Noise-mask shader |
| Save / Load game | G-HUD-09 | L | Full state serialisation |
| Options menu | G-HUD-10 | M | Settings persistence |
| Screen wipe transitions | G-REN-11 | M | Melt transition |
| Cheat codes | G-GS-10 | S | Key sequence buffer |

**Estimated effort**: 6–10 weeks

---

## Total Gap Count by Phase

| Phase | P1 Tasks | P2 Tasks | P3/P4 Tasks | Total |
|-------|----------|----------|-------------|-------|
| 1 Foundation | 6 | 1 | 0 | 7 |
| 2 Playable World | 7 | 1 | 0 | 8 |
| 3 Player Systems | 9 | 2 | 1 | 12 |
| 4 Enemies | 10 | 4 | 0 | 14 |
| 5 Interactivity | 10 | 2 | 0 | 12 |
| 6 Audio | 4 | 3 | 0 | 7 |
| 7 Polish | 0 | 5 | 12 | 17 |
| **Total** | **46** | **18** | **13** | **77** |

---

## Key Architectural Decisions

### 1. Tic-Based vs Frame-Based Update

DOOM runs at a fixed 35 tics/second. Physics, AI, and gameplay are all tic-accurate. Rendering runs as fast as possible.

**Recommendation**: Implement a fixed timestep game loop:
```python
TICS_PER_SEC = 35
TIC_DURATION = 1.0 / TICS_PER_SEC
accumulated_time = 0.0

while running:
    accumulated_time += get_frame_time()
    while accumulated_time >= TIC_DURATION:
        game_tick()            # physics, AI, specials
        accumulated_time -= TIC_DURATION
    render_frame()             # runs at display rate
```

### 2. Moving Sector Mesh Regeneration

Portal wall meshes are currently pre-built at level load. Moving sectors require mesh updates.

**Recommendation**: Make `WallModel` regenerate its mesh lazily when the bounding sector's floor/ceiling height changes. Store the last-used heights and rebuild only when they differ.

### 3. Actor/Blockmap Integration

The blockmap needs to store both linedefs (for physics) and actors (for AI/pickup/combat). Actors move, so they must be re-registered in the blockmap each tic.

**Recommendation**: A two-layer blockmap:
- Static layer: linedefs (built once at load, rebuilt on moving sector change).
- Dynamic layer: actors (cleared and rebuilt each tic from the actor list).

### 4. Sprite vs 3D Approach

DOOM used 2D sprites for all dynamic objects. Options:
- **Billboard sprites** (recommended): Use Raylib's `DrawBillboard()`. Fast, authentic look.
- **3D models**: Higher visual fidelity but diverges from DOOM aesthetic.

Sprites should use the WAD's patch data decoded to RGBA with alpha testing.

### 5. WAD Dependency

Running actual DOOM maps requires the DOOM IWAD (`DOOM.WAD` or `DOOM1.WAD`). The engine should:
- Accept an IWAD path via command line argument or config file.
- Fall back to the existing test level if no WAD is provided.
- Support FreeDOOM as a free alternative IWAD.

---

## Files to Create

| New File | Purpose |
|----------|---------|
| `wad/wad_reader.py` | WAD binary parser |
| `wad/map_parser.py` | VERTEXES/LINEDEFS/SIDEDEFS/SECTORS/THINGS parsing |
| `wad/texture_loader.py` | Patch composite + flat texture loading from WAD |
| `physics/blockmap.py` | Linedef + actor spatial index |
| `physics/collision.py` | Circle vs linedef, slide, step-up |
| `physics/sector_query.py` | Point-in-sector via BSP |
| `actors/actor.py` | Base Actor class |
| `actors/state_machine.py` | State/StateDefinition/tick_actor |
| `actors/spawner.py` | Thing type → Actor mapping |
| `actors/player_state.py` | Health, armour, ammo, weapons, keys |
| `actors/monsters/*.py` | Per-monster state tables and action functions |
| `combat/hitscan.py` | Ray attack, auto-aim |
| `combat/projectile.py` | Missile movement and explosion |
| `combat/doom_rng.py` | Fixed RNG table |
| `rendering/sprite_renderer.py` | Billboard + angle-frame selection |
| `rendering/sprite_loader.py` | WAD patch → Raylib texture |
| `audio/sound_system.py` | 8-channel sound playback |
| `audio/music_system.py` | Level music streaming |
| `ui/hud.py` | Status bar rendering |
| `ui/menu.py` | Menu stack system |
| `ui/messages.py` | In-game message display |
| `ui/intermission.py` | Post-level screen |
| `level/special_linedefs.py` | Action type registry and handlers |
| `level/moving_sector.py` | Animated floor/ceiling system |
| `level/special_sectors.py` | Per-tic sector effects |
| `game_session.py` | Top-level game state, counters, difficulty |
