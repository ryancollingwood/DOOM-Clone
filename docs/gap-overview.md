# Gap Overview — Feature Matrix

Quick-reference matrix of every major DOOM (1994) system, its implementation status in this clone, and its priority for achieving gameplay parity.

## Status Key

| Symbol | Meaning |
|--------|---------|
| `[x]` | Implemented |
| `[~]` | Partial / placeholder |
| `[ ]` | Not implemented |

## Priority Key

| Priority | Rationale |
|----------|-----------|
| **P1 — Blocker** | Game is not playable without this |
| **P2 — Core** | Significantly degrades experience if missing |
| **P3 — Important** | Notable difference from DOOM but game still runs |
| **P4 — Polish** | Authentic but non-essential for comparable gameplay |

---

## Feature Matrix

### Rendering

| Feature | Status | Priority | Complexity | Notes |
|---------|--------|----------|------------|-------|
| BSP-based level geometry | `[x]` | P1 | — | Complete |
| Textured walls | `[x]` | P1 | — | Complete |
| Textured floors/ceilings | `[x]` | P1 | — | Complete |
| Portal/sector height steps | `[x]` | P1 | — | Complete |
| Per-sector lighting level | `[ ]` | P2 | S | Each sector needs a `light_level` 0–255 |
| Sprite billboarding | `[ ]` | P1 | L | Enemies, items, decorations, projectiles |
| Wall texture offsets (X/Y) | `[ ]` | P2 | S | Per-linedef horizontal/vertical shift |
| Animated wall textures | `[ ]` | P3 | M | Texture animation sequences (fire, water) |
| Animated flat textures | `[ ]` | P3 | M | Animated floor/ceiling (nukage, water) |
| Sky texture rendering | `[ ]` | P2 | M | F_SKY1 flat triggers sky ceiling |
| Automap | `[~]` | P3 | M | Minimap exists; needs proper DOOM automap behaviour |
| Fuzz/spectre effect | `[ ]` | P4 | M | Partial translucency mask for spectres |
| Colormap / light diminishing | `[ ]` | P2 | M | Distance-based darkening per sector light level |
| Weapon sprites on HUD | `[ ]` | P1 | M | Foreground weapon sprite layer |
| Screen wipe transitions | `[ ]` | P4 | M | Melt / burn transition between levels |

### Player Physics

| Feature | Status | Priority | Complexity | Notes |
|---------|--------|----------|------------|-------|
| Wall collision detection | `[ ]` | P1 | M | Slide along walls, not clip through |
| Floor/ceiling collision | `[ ]` | P1 | S | Clamp to sector floor, block at ceiling |
| Sector floor tracking | `[ ]` | P1 | S | Player stands on floor height of current sector |
| Step-up (staircase) | `[ ]` | P1 | S | Auto-step up to 24 units max |
| Gravity | `[ ]` | P1 | S | Fall when no floor beneath |
| Running speed | `[~]` | P2 | S | Camera moves; needs DOOM-accurate speed tuning |
| Use action (doors/switches) | `[ ]` | P1 | M | E key activates linedefs in range |
| Player death / respawn | `[ ]` | P1 | S | Health reaches 0 → death state |
| Momentum / deceleration | `[ ]` | P3 | S | DOOM has friction/momentum model |
| No freelook (vanilla) | `[~]` | P4 | S | Vanilla DOOM had no vertical look; optional |

### Combat

| Feature | Status | Priority | Complexity | Notes |
|---------|--------|----------|------------|-------|
| Weapon system | `[ ]` | P1 | L | Slot-based, switch animations, fire logic |
| Hitscan attacks | `[ ]` | P1 | M | Pistol, shotgun, chaingun — instant ray |
| Projectile attacks | `[ ]` | P1 | M | Rockets, plasma, fireballs — moving actors |
| Melee attacks | `[ ]` | P2 | S | Fist, chainsaw — close-range hitscan |
| Damage model | `[ ]` | P1 | S | Random damage rolls, armour absorption |
| Player health & armour | `[ ]` | P1 | S | Tracked, shown on HUD |
| Ammo system | `[ ]` | P1 | S | 4 ammo types: bullets, shells, rockets, cells |
| Weapon pickup | `[ ]` | P1 | S | Spawn with pistol, pick up others |
| Splash damage | `[ ]` | P2 | S | Rocket/BFG area damage with falloff |
| Telefrag | `[ ]` | P3 | S | Teleport into actor kills both |

### Monster AI

| Feature | Status | Priority | Complexity | Notes |
|---------|--------|----------|------------|-------|
| Monster spawning (map Things) | `[ ]` | P1 | M | Load Thing data, place actors at start |
| Monster state machine | `[ ]` | P1 | L | Spawn→See→Chase→Attack→Pain→Death states |
| Line-of-sight checks | `[ ]` | P1 | M | BSP-aware sight query |
| Chase / pathfinding | `[ ]` | P1 | M | Move toward player, navigate around walls |
| Alert propagation (noise) | `[ ]` | P2 | S | Sound alerts nearby monsters |
| Monster-monster interaction | `[ ]` | P2 | M | Infighting when hit by other monster |
| Resurrection (Arch-vile) | `[ ]` | P3 | M | Raise dead corpses |
| All 9 original monsters | `[ ]` | P1 | XL | Zombie, Shotguy, Imp, Demon, Spectre, Lost Soul, Cacodemon, Baron, Cyberdemon |

### Audio

| Feature | Status | Priority | Complexity | Notes |
|---------|--------|----------|------------|-------|
| Sound effects | `[ ]` | P1 | M | Per-action WAV/OGG playback |
| Positional audio | `[ ]` | P2 | M | Pan left/right based on actor position |
| Background music (MIDI) | `[ ]` | P2 | M | Per-level MUS/MIDI track |
| OPL2 synthesis (authentic) | `[ ]` | P4 | XL | Accurate OPL2/Adlib emulation |
| Sound priority system | `[ ]` | P3 | S | Higher-priority sounds pre-empt lower ones |
| Distance attenuation | `[ ]` | P2 | S | Volume falls off with distance |

### HUD & UI

| Feature | Status | Priority | Complexity | Notes |
|---------|--------|----------|------------|-------|
| Status bar | `[ ]` | P1 | M | Health, armour, ammo, face, keys |
| Weapon numbers | `[ ]` | P1 | S | Ammo count per slot |
| Key icons | `[ ]` | P2 | S | Red/yellow/blue key/skull display |
| Main menu | `[ ]` | P1 | M | New game, load, save, options, quit |
| Episode/skill select | `[ ]` | P1 | S | 4 episodes × 5 skills |
| Pause menu | `[ ]` | P1 | S | ESC pauses game |
| Intermission screen | `[ ]` | P2 | M | Level complete stats: kills, items, secrets |
| In-game messages | `[ ]` | P2 | S | "You picked up..." text overlay |
| Save / load game | `[ ]` | P3 | L | Serialise full game state |
| Options menu | `[ ]` | P3 | M | Screen size, mouse sensitivity, sound |

### Level System

| Feature | Status | Priority | Complexity | Notes |
|---------|--------|----------|------------|-------|
| WAD file parser | `[ ]` | P1 | L | Read IWAD/PWAD lump structure |
| MAP/ExMy level loading | `[ ]` | P1 | L | VERTEXES, LINEDEFS, SIDEDEFS, SECTORS, THINGS |
| Special linedef actions | `[ ]` | P1 | XL | Doors, lifts, crushers, teleports, exits |
| Special sector types | `[ ]` | P1 | L | Damage floors, secret areas, light flicker |
| Multiple levels / E1M1–E3M9 | `[ ]` | P1 | M | Level sequencing and loading |
| Secret exit triggers | `[ ]` | P2 | S | Alternate exit linedef type |
| Level timer | `[ ]` | P3 | S | Elapsed time tracked for intermission |
| Blockmap | `[ ]` | P2 | M | Spatial index for fast collision queries |
| REJECT table | `[ ]` | P3 | M | Pre-computed LOS table for monster AI |

### Game Systems

| Feature | Status | Priority | Complexity | Notes |
|---------|--------|----------|------------|-------|
| Thing spawning (items) | `[ ]` | P1 | M | All pickup items placed from THINGS lump |
| Item pickup logic | `[ ]` | P1 | M | Touch item actor → apply effect |
| Keys (red/yellow/blue) | `[ ]` | P1 | S | Carried in inventory, needed for doors |
| Power-ups | `[ ]` | P2 | M | Invulnerability, berserk, invis, rad suit, map |
| Difficulty scaling | `[ ]` | P2 | M | Monster count/health/damage per skill level |
| Cooperative multiplayer | `[ ]` | P4 | XL | Out of scope for single-player parity |
| Deathmatch | `[ ]` | P4 | XL | Out of scope for single-player parity |
| Demo playback | `[ ]` | P4 | L | LMP demo format |
| God mode / IDKFA cheats | `[ ]` | P4 | S | Debug cheats |

---

## Priority Summary

| Priority | Count | Description |
|----------|-------|-------------|
| P1 — Blocker | 31 | Must implement for a playable game |
| P2 — Core | 18 | Implement for a good DOOM-like experience |
| P3 — Important | 14 | Implement for authenticity |
| P4 — Polish | 9 | Nice to have, low gameplay impact |
| **Total gaps** | **72** | |

The current engine covers roughly **8%** of the total feature surface needed for DOOM-comparable gameplay. The rendering foundation is solid; almost all gaps are in gameplay, physics, AI, audio, and UI systems.

---

## Implementation Order (High Level)

1. **Player physics** — collision, gravity, sector floor tracking (game is unplayable otherwise)
2. **Level loading (WAD)** — get real DOOM maps in-engine
3. **Special linedefs** — doors, exits (level progression)
4. **Sprite renderer** — items/enemies visible
5. **HUD / status bar** — health, ammo feedback
6. **Weapon system** — player can shoot
7. **Monster AI** — enemies react and attack
8. **Audio** — sound and music
9. **Menus / UI** — proper game flow
10. **Polish** — lighting, animations, effects

See [gap-implementation-roadmap.md](gap-implementation-roadmap.md) for the full phased plan.
