# Gap: Monster AI

## What DOOM Does

DOOM's monster AI is a state machine driven by the same tic-based engine as everything else. Each monster has a set of states (defined in `info.c` in the original source), each referencing a sprite frame, a duration in tics, and an optional action function.

---

## Current State

No actors, no monster system, no AI of any kind exists. The level contains only static geometry.

---

## Gaps

### G-AI-01 — Actor System (P1, L)

**What DOOM does**: Every dynamic object in DOOM (monsters, items, projectiles, decorations) is a `mobj_t` (map object). Key fields:

| Field | Description |
|-------|-------------|
| `x, y, z` | World position |
| `angle` | Facing angle (0–360°) |
| `radius` | Collision radius |
| `height` | Collision height |
| `health` | Current health |
| `flags` | `MF_SOLID`, `MF_SHOOTABLE`, `MF_MISSILE`, `MF_PICKUP`, etc. |
| `state` | Current state in the state machine |
| `target` | The actor this one is pursuing/attacking |
| `tics` | Ticks remaining in current state |
| `momx, momy` | Horizontal momentum |

**Gap**: Implement an `Actor` base class/dataclass and a global actor list managed by the game engine.

```python
@dataclass
class Actor:
    x: float; y: float; z: float
    angle: float = 0.0
    radius: float = 20.0
    height: float = 56.0
    health: int = 100
    flags: int = 0   # MF_SOLID | MF_SHOOTABLE etc.
    state: 'ActorState' = None
    target: 'Actor' = None
    tics: int = 0
    vx: float = 0.0; vy: float = 0.0; vz: float = 0.0
```

**Dependencies**: Requires the sector/blockmap system to place actors and check collision.

---

### G-AI-02 — State Machine (P1, L)

**What DOOM does**: Each actor type has a list of states. A state specifies:
- Sprite name + frame letter (for rendering)
- Duration in tics (-1 = infinite)
- Optional action function to call on entry or each tic
- Next state to transition to after duration expires

Example states for the Zombie:
```
POSS_STND  → POSS_STND2 (idle, loops)
POSS_STND2 → POSS_STND  
POSS_RUN1  → POSS_RUN2  (A_Chase called each tic)
...
POSS_DIE1  → POSS_DIE2  (A_Scream on entry)
...
POSS_DIE5  → POSS_XDIE1 (A_Fall)
```

**Gap**: A `StateDefinition` class and a per-actor-type state table. Each tic, decrement actor's `tics`; when 0, transition to `next_state` and call `action_fn`.

```python
@dataclass
class StateDefinition:
    sprite: str           # e.g. "POSS"
    frame: int            # 0=A, 1=B, ...
    tics: int             # -1 = infinite
    action: Callable = None
    next_state: str = None

def tick_actor(actor: Actor, state_table: dict):
    actor.tics -= 1
    if actor.tics == 0:
        s = state_table[actor.state.next_state]
        actor.state = s
        actor.tics = s.tics
        if s.action:
            s.action(actor)
```

---

### G-AI-03 — Line-of-Sight (P1, M)

**What DOOM does**: `P_CheckSight(actor1, actor2)` — can actor1 see actor2?

Algorithm:
1. Quick reject: consult the REJECT table (precomputed sector-to-sector visibility table from the WAD).
2. Cast a 2D ray in map space from actor1 to actor2.
3. Step through BSP tree: if the ray crosses an opaque linedef (solid wall, or a portal where the gap is insufficient), return false.
4. Also check that the vertical angle of the ray falls within the opening (floor/ceiling gap of portals).

**Gap**: Implement `check_sight(a: Actor, b: Actor) -> bool`.

**Implementation notes**:
- The BSP tree already exists and can be reused for ray traversal.
- Start without the REJECT table optimisation (brute-force linedef crossing check).
- Ray in 2D: parametric form, test against each linedef between the two actors' BLOCKMAP cells.
- Add REJECT table lookup later as an optimisation once WAD loading provides the lump.

---

### G-AI-04 — Monster Alert / Noise Wake-Up (P2, S)

**What DOOM does**:
- When the player fires a weapon, noise is generated.
- All monsters in the same sector as the noise, or in nearby sectors connected without a blocking solid wall, are alerted.
- Alert = transition from `STND` (idle) state to `SEE` (chase) state.
- Monsters can also alert each other: a monster that sees the player and roars will wake nearby monsters.

**Gap**: Implement `noise_alert(origin_sector, source_actor)`:
- BFS/flood-fill through connected sectors (via two-sided linedefs).
- Stop at closed (impassable) sector boundaries.
- Set `monster.target = player` and transition to chase state for all reached monsters.

---

### G-AI-05 — Chase / Pathfinding (P1, M)

**What DOOM does**: `A_Chase` — the standard monster movement action, called each tic while chasing.

Algorithm:
1. If target is dead or missing: clear target, return to idle.
2. If `reaction_time > 0`: decrement and return (newly alerted monsters have a reaction delay).
3. Check if a melee attack is in range: if so, enter attack state.
4. Check if a missile attack is ready (random chance): if so, enter attack state.
5. Move toward target: try to move along the target direction. If blocked, try 45° and 90° deviations (`A_Chase` uses a fixed set of 8 direction attempts).
6. If move succeeds: update position, play footstep sound occasionally.

**Gap**: Implement `a_chase(actor)` action function that moves the actor toward its `target`.

**Implementation notes**:
- Monster movement is 2D (horizontal only).
- No true pathfinding — DOOM uses a "try to move toward target, try slight angles on failure" heuristic.
- Collision: actors push other actors aside (except when blocked by a solid actor).
- Speed: each monster type has a fixed speed (e.g., Imp = 8 mu/tic, Baron = 8, Cyberdemon = 16).

---

### G-AI-06 — Monster Attack Actions (P1, M)

**What DOOM does**: Each monster has attack actions triggered from its attack state. Examples:

| Monster | Action | Attack |
|---------|--------|--------|
| Zombie | `A_PosAttack` | Hitscan bullet, 3–15 damage |
| Shotgun Zombie | `A_SPosAttack` | 3 hitscan pellets |
| Imp | `A_TroopAttack` | Melee or fireball |
| Demon | `A_SargAttack` | Melee bite |
| Cacodemon | `A_HeadAttack` | Fireball |
| Baron | `A_BruisAttack` | Melee or fireball |
| Cyberdemon | `A_CyberAttack` | 3 rockets |
| Spider Mastermind | `A_SpidAttack` | Chaingun |

**Gap**: Implement per-monster attack action functions. Most reuse the hitscan and projectile systems from combat (gap-combat.md G-CMB-04, G-CMB-05).

---

### G-AI-07 — Monster Pain & Death (P1, M)

**What DOOM does**:
- When a monster takes damage, it has a `pain_chance` (0–255). `P_Random() < pain_chance` → enter PAIN state briefly before returning to chase.
- When health ≤ 0: enter DEATH or XDEATH state (gibbing when overkill).
- Death state plays a death sound, then transitions to a final DEAD state (static corpse sprite on the floor).
- Corpses remain in the level and can be walked over (they become non-solid after a few tics).

**Gap**:
- `apply_damage(actor, amount)`: subtract health, check pain chance, check death.
- In death state action (`A_Fall`): remove `MF_SOLID` flag so the corpse becomes passable.

---

### G-AI-08 — Monster Infighting (P2, M)

**What DOOM does**: When a monster is damaged by a projectile from another monster (e.g., a Baron's fireball hits an Imp), the Imp retargets to the Baron. This causes monsters to fight each other when caught in cross-fire.

**Gap**: In `apply_damage(victim, damage, source)`:
- If source is a monster and `source != victim.target`: set `victim.target = source`.
- The victim will then chase and attack the source on its next `A_Chase` tick.

---

### G-AI-09 — All 9 Original DOOM Monsters (P1, XL)

Each monster requires: health, speed, radius, height, pain_chance, attack damage, state table, sprite frames, and sounds. This is primarily a data/content task once the AI framework (G-AI-01 through G-AI-07) is in place.

**Monster roster for DOOM Episode 1–3**:

| Monster | Health | Speed | Radius | Key Behaviour |
|---------|--------|-------|--------|---------------|
| Zombie (Former Human) | 20 | 8 | 20 | Pistol hitscan |
| Shotgun Zombie | 30 | 8 | 20 | 3-pellet hitscan |
| Imp | 60 | 8 | 20 | Melee + fireball |
| Demon | 150 | 10 | 30 | Fast melee bite |
| Spectre | 150 | 10 | 30 | Demon + fuzz render |
| Lost Soul | 100 | 8 | 16 | Charging skull |
| Cacodemon | 400 | 8 | 31 | Floating, fireball |
| Baron of Hell | 1000 | 8 | 24 | Tough, fireball + melee |
| Cyberdemon | 4000 | 16 | 40 | Rocket-launching boss |
| Spider Mastermind | 3000 | 12 | 128 | Chaingun boss |

*(Super Shotgun Zombie, Arch-Vile, Mancubus, Revenant, Hell Knight, Pain Elemental are DOOM 2 monsters — out of scope for DOOM 1 parity.)*

---

## Actor System Architecture

```
GameEngine
    ├── actor_list: list[Actor]      # all active actors
    ├── blockmap: Blockmap           # spatial index for actors
    │
    ├── update():
    │   └── for actor in actor_list:
    │       ├── tick_actor(actor, state_tables)
    │       ├── move_actor(actor)     # apply vx/vy, collision
    │       └── sector_update(actor) # update z to floor
    │
    └── Actor
        ├── state: StateDefinition
        ├── target: Actor
        └── flags: int (MF_*)
```

---

## Summary Table

| Gap | Priority | Complexity |
|-----|----------|------------|
| G-AI-01 Actor system | P1 | L |
| G-AI-02 State machine | P1 | L |
| G-AI-03 Line-of-sight | P1 | M |
| G-AI-04 Monster alert / noise | P2 | S |
| G-AI-05 Chase / pathfinding | P1 | M |
| G-AI-06 Monster attack actions | P1 | M |
| G-AI-07 Pain & death | P1 | M |
| G-AI-08 Infighting | P2 | M |
| G-AI-09 All 9 monsters (data) | P1 | XL |
