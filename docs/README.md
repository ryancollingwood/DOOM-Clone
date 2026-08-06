# DOOM Clone — Gameplay Gap Analysis

This directory contains a structured gap analysis comparing the current DOOM Clone implementation against the original **DOOM (1994)** feature set. The goal is to identify what needs to be built to achieve comparable gameplay.

## Current State

The engine has a solid foundation:

- BSP-based 3D level renderer with sector/portal geometry
- First-person camera with mouse-look
- Texture-mapped walls and floors/ceilings
- Dynamic wall shading based on light direction
- 2D minimap overlay
- Performance-optimised traversal and mesh generation

The level renderer is functionally complete for static geometry. Everything beyond static geometry — player physics, enemies, weapons, audio, HUD, menus — is absent.

## Documents

| File | Topic |
|------|-------|
| [gap-overview.md](gap-overview.md) | Feature matrix and priority summary |
| [gap-player-physics.md](gap-player-physics.md) | Movement, collision, gravity, sector interaction |
| [gap-rendering.md](gap-rendering.md) | Sprites, automap, sector lighting, sky, effects |
| [gap-combat.md](gap-combat.md) | Weapons, projectiles, hitscan, enemies |
| [gap-ai.md](gap-ai.md) | Monster AI, pathfinding, state machines |
| [gap-audio.md](gap-audio.md) | Sound effects, music (OPL/MIDI), positional audio |
| [gap-hud-ui.md](gap-hud-ui.md) | HUD, menus, intermission, status bar |
| [gap-level-system.md](gap-level-system.md) | WAD loading, level progression, special sectors/linedefs |
| [gap-game-systems.md](gap-game-systems.md) | Items, pickups, inventory, game state, difficulty |
| [gap-implementation-roadmap.md](gap-implementation-roadmap.md) | Phased implementation plan with dependencies |

## How to Read This

Each gap document follows the same structure:

1. **What DOOM does** — original behaviour, sourced from the Doom engine design
2. **What we have** — current implementation status
3. **Gap** — specific missing pieces
4. **Implementation notes** — technical approach, edge cases, complexity estimate

Complexity is rated **S / M / L / XL**:

- **S** — days, self-contained
- **M** — 1–2 weeks, limited dependencies
- **L** — 2–4 weeks, crosses multiple systems
- **XL** — a month+, architectural impact
