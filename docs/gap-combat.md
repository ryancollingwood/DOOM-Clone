# Gap: Combat Systems

## What DOOM Does

DOOM's combat consists of the player wielding weapons that deal damage to enemies (and vice versa) through two attack mechanics: **hitscan** (instant-hit ray) and **projectiles** (moving actor). Damage is randomised within ranges, and armour absorbs a portion.

---

## Current State

None of the combat systems are implemented. The player has no weapons, deals no damage, and cannot be harmed.

---

## Gaps

### G-CMB-01 — Player Health & Armour (P1, S)

**What DOOM does**:
- `health`: starts at 100, max 200 (with Megasphere). Reaches 0 → dead.
- `armour`: starts at 0, max 200. Green armour absorbs 33% of damage; blue armour 50%.
- `armour_type`: 0 = none, 1 = green (security), 2 = blue (combat).
- Both displayed in the status bar.

**Gap**: A `PlayerState` class tracking `health`, `armour`, `armour_type`.

**Implementation notes**:
```python
@dataclass
class PlayerState:
    health: int = 100
    armour: int = 0
    armour_type: int = 0   # 0=none, 1=green, 2=blue

    def apply_damage(self, raw: int) -> None:
        saved = raw * [0, 0.33, 0.50][self.armour_type]
        self.armour -= int(saved)
        if self.armour < 0:
            # over-spent armour carries over as damage
            raw += self.armour  # armour is negative
            self.armour = 0
            self.armour_type = 0
        self.health -= (raw - int(saved))
```

---

### G-CMB-02 — Ammo System (P1, S)

**What DOOM does**:
- 4 ammo types: `bullets`, `shells`, `rockets`, `cells`
- Each has a max capacity (200, 50, 50, 300 normally; doubled with Backpack)
- Weapons consume specific amounts per shot

**Gap**: Track ammo counts in `PlayerState`.

```python
ammo: dict = field(default_factory=lambda: {
    'bullets': 50,
    'shells': 0,
    'rockets': 0,
    'cells': 0,
})
ammo_max: dict = field(default_factory=lambda: {
    'bullets': 200,
    'shells': 50,
    'rockets': 50,
    'cells': 300,
})
```

---

### G-CMB-03 — Weapon Slot System (P1, L)

**What DOOM does**:
- 7 weapon slots (0 = fist/chainsaw overlapping slot 1, then 1–7)
- Player spawns with fist + pistol (slot 1 active)
- Weapons are picked up by walking over them
- Switch between weapons via number keys 1–7; or auto-switch to best available weapon on pickup

**DOOM's 9 weapons**:

| Slot | Weapon | Ammo Type | Ammo/shot | Attack Type |
|------|--------|-----------|-----------|-------------|
| 1 | Fist | — | — | Melee hitscan |
| 1 | Chainsaw | — | — | Melee hitscan (continuous) |
| 2 | Pistol | Bullets | 1 | Hitscan |
| 3 | Shotgun | Shells | 1 (7 pellets) | Hitscan spread |
| 3 | Super Shotgun | Shells | 2 (20 pellets) | Hitscan spread (DOOM 2) |
| 4 | Chaingun | Bullets | 1/tic | Hitscan (auto) |
| 5 | Rocket Launcher | Rockets | 1 | Projectile + splash |
| 6 | Plasma Rifle | Cells | 1 | Projectile |
| 7 | BFG 9000 | Cells | 40 | Projectile + tracers |

**Gap**: A `Weapon` class and `weapons_owned` set in `PlayerState`. Each weapon defines its attack function, ammo consumption, fire delay (tics), and sprite frames.

**Implementation notes**:
- Represent each weapon as a dataclass with: `slot`, `ammo_type`, `ammo_per_shot`, `fire_tics`, `attack_fn`, `sprite_prefix`.
- Current weapon state machine: `READY → FIRING → LOWERING → RAISING → READY`
- Weapon bob and fire animation handled by the rendering system (G-REN-09).

---

### G-CMB-04 — Hitscan Attack (P1, M)

**What DOOM does**:
- Cast a ray from the player's eye position in the aim direction.
- The ray is 2D in the XY map plane; vertical aim uses a slope derived from the target's height (auto-aim).
- On hit: find the closest actor or wall along the ray.
- If actor: apply damage. If wall: spawn a puff sprite (bullet mark).

**Auto-aim**: DOOM scans a cone of ±45° (autoaim) around the player's yaw for the closest actor in the vertical aim range. If found, the shot is redirected to that actor's centre height.

**Gap**: Implement `hitscan_attack(origin, angle, damage_range, spread)`:
1. Optional auto-aim pass: scan actors in a forward cone, find closest within aim slope bounds.
2. Cast ray in map XY: test all linedefs and actors in blockmap cells along the ray.
3. Apply `random.randint(damage_range[0], damage_range[1])` damage to hit actor.
4. Spawn puff/blood sprite at impact point.

**Implementation notes**:
- Use the blockmap for efficient ray traversal (DDA along grid cells).
- Pellet spread (shotgun): apply independent random `spread_angle` ±5.6° per pellet.
- Blood sprites: different colour for demons vs humans.

---

### G-CMB-05 — Projectile Attack (P1, M)

**What DOOM does**:
- Spawn a new `Actor` at the attacker's position facing the target direction.
- Each tic, move the projectile by its `speed` in the facing direction.
- On colliding with a wall or actor: explode (apply radius damage and spawn explosion sprite).

**Key projectiles**:

| Weapon | Speed (mu/tic) | Damage | Radius |
|--------|---------------|--------|--------|
| Rocket | 20 | 10–160 splash | 128 |
| Plasma ball | 25 | 5–15 | 0 |
| BFG ball | 25 | 100–800 | 0 (+tracers) |
| Imp fireball | 10 | 3–24 | 0 |
| Baron fireball | 15 | 8–70 | 0 |
| Cacodemon fireball | 12.5 | 5–40 | 0 |

**Gap**: Implement projectile actors with a movement tick, collision detection against walls (linedefs) and actors (radius check), and an explosion handler.

**Implementation notes**:
- Projectiles are the same actor system as monsters (see gap-ai.md) with a `MF_MISSILE` flag.
- Radius damage: for each actor within `explosion_radius`, compute distance, scale damage by `(1 - distance / radius)`, apply.
- Splash damage can harm the player (and is the source of rocket jumping in practice, though not intentional in DOOM 1).

---

### G-CMB-06 — Melee Attack (P2, S)

**What DOOM does**:
- Fist: damage = `random.randint(1, 10) * 2` (with berserk: `*10`)
- Chainsaw: continuous attack at short range, deals `random.randint(1, 10) * 2` per tic
- Range = 64 map units; checks for an actor within this range directly in front
- No ammo consumed

**Gap**: A `melee_attack(range, damage_range)` function that checks for an actor within `range` directly ahead and applies damage.

---

### G-CMB-07 — Damage Randomisation (P1, S)

**What DOOM does**:
- Uses a fixed 256-entry lookup table (`rndtable`) with a rolling index for all random numbers.
- This ensures reproducible demo playback. `P_Random()` returns the next byte.
- Damage = `base * (P_Random() % max_random + 1)`

**Gap**: Implement a `DoomRNG` class with the fixed table and an `rnd()` method. Use this everywhere randomness is needed (damage, monster AI decisions, spread angles) to allow demo-accurate playback.

```python
RND_TABLE = [0, 8, 109, 220, ...]  # 256 entries from Doom source
class DoomRNG:
    def __init__(self): self.index = 0
    def rnd(self) -> int:
        val = RND_TABLE[self.index % 256]
        self.index = (self.index + 1) % 256
        return val
```

---

### G-CMB-08 — Splash Damage (P2, S)

**What DOOM does**:
- Rocket explosions deal damage to all actors within `128` map units.
- Damage = `128 - distance` (capped at 0).
- Damage is further multiplied by `P_Random()`.
- Walls do not block splash damage in vanilla DOOM (intentional).

**Gap**: `radius_attack(origin, radius, max_damage, source_actor)` function iterating all actors in nearby blockmap cells.

---

### G-CMB-09 — Player Death (P1, S)

**What DOOM does**:
- Health reaches 0: player enters death state.
- Camera pitch drops to -30° (viewing the ground).
- Death sound plays.
- Input is locked (except for pressing Use/Fire to respawn in multiplayer, or waiting for intermission).
- After a delay, the level restarts (or loads saved game in single player).

**Gap**: Detect `player.health <= 0`, trigger death animation (lower view angle over time), lock input, then reload level after delay.

---

## Combat Interaction Flow

```
Player presses Fire
    ↓
WeaponState: READY → FIRING
    ↓
attack_fn() called:
    hitscan_attack()  or  spawn_projectile()
    ↓
    Projectile: each tic, move, check collision
    Hitscan: immediate ray test
    ↓
    Hit actor: actor.apply_damage(amount)
        ↓ health ≤ 0 → actor death state
    Hit wall:  spawn puff sprite
    ↓
WeaponState: FIRING → READY (after fire_tics)
```

---

## Summary Table

| Gap | Priority | Complexity |
|-----|----------|------------|
| G-CMB-01 Health & armour | P1 | S |
| G-CMB-02 Ammo system | P1 | S |
| G-CMB-03 Weapon slots | P1 | L |
| G-CMB-04 Hitscan attack | P1 | M |
| G-CMB-05 Projectile attack | P1 | M |
| G-CMB-06 Melee attack | P2 | S |
| G-CMB-07 Damage randomisation (RNG) | P1 | S |
| G-CMB-08 Splash damage | P2 | S |
| G-CMB-09 Player death | P1 | S |
