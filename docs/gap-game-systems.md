# Gap: Game Systems

## What DOOM Does

Beyond rendering and combat, DOOM has a set of game-state systems that tie together the player experience: items and pickups, keys, power-ups, difficulty scaling, and game flow. These are largely data-driven and sit on top of the actor system.

---

## Current State

None of these systems are implemented. The player has no inventory, the level has no interactable objects, and there is no overall game state management.

---

## Gaps

### G-GS-01 — Game State Manager (P1, S)

**What DOOM does**: The engine always has a global `gamestate` that determines which logic runs:

| State | Description |
|-------|-------------|
| `GS_TITLESCREEN` | Demo/title cycling |
| `GS_LEVEL` | Active gameplay |
| `GS_INTERMISSION` | Post-level stats |
| `GS_FINALE` | Episode end story text |

**Gap**: A `GameState` enum and dispatcher in `engine.py` that routes update/draw calls to the correct subsystem.

```python
class GameState(Enum):
    TITLE = "title"
    MENU = "menu"
    PLAYING = "playing"
    INTERMISSION = "intermission"
    FINALE = "finale"
```

---

### G-GS-02 — Thing Spawning (P1, M)

**What DOOM does**: When a level loads, all `THINGS` lump entries are iterated. Each Thing has a `type` number that maps to an actor definition (`mobjinfo` in the source). The actor is spawned at the Thing's (x, y) position facing the Thing's angle.

**Key thing types**:

| Type | Actor |
|------|-------|
| 1 | Player 1 start |
| 2 | Player 2 start |
| 3 | Player 3 start |
| 4 | Player 4 start |
| 11 | Deathmatch start |
| 14 | Teleport landing |
| 3004 | Zombie |
| 9 | Shotgun zombie |
| 3001 | Imp |
| 3002 | Demon |
| 58 | Spectre |
| 3006 | Lost Soul |
| 3005 | Cacodemon |
| 3003 | Baron of Hell |
| 16 | Cyberdemon |
| 7 | Spider Mastermind |
| 2001 | Shotgun |
| 2002 | Chaingun |
| 2003 | Rocket launcher |
| 2004 | Plasma rifle |
| 2006 | BFG 9000 |
| 2005 | Chainsaw |
| 2011 | Health bonus (+1) |
| 2012 | Stimpack (+10) |
| 2013 | Medikit (+25) |
| 2014 | Soul sphere (+100 health) |
| 2015 | Armour bonus (+1 armour) |
| 2018 | Green armour (100 armour) |
| 2019 | Blue armour (200 armour) |
| 2022 | Invulnerability sphere |
| 2023 | Berserk pack |
| 2024 | Partial invisibility |
| 2025 | Radiation suit |
| 2026 | Computer map |
| 2028 | Light amplification visor |
| 5 | Blue skull key |
| 6 | Yellow skull key |
| 13 | Red skull key |
| 38 | Blue keycard |
| 39 | Yellow keycard |
| 40 | Red keycard |
| 2048 | Bullets |
| 2007 | Shell box |
| etc. | ... |

**Gap**: A `ThingSpawner` that maps thing type numbers to actor constructors and places them in the world.

---

### G-GS-03 — Item Pickup (P1, M)

**What DOOM does**: When the player overlaps an item actor (within the player's radius, and the item's `MF_PICKUP` flag is set), `P_TouchSpecialThing` is called:
- Apply the item's effect (add health, ammo, key, etc.).
- If item is not a power-up that respawns (no `MF_COUNTITEM`), remove the actor from the world.
- Play the appropriate pickup sound.
- Display a pickup message.

**Gap**: Each tic, check for player/item overlap using radius test in the blockmap. Map item type to pickup effect function.

```python
PICKUP_EFFECTS = {
    ThingType.HEALTH_BONUS: lambda p: add_health(p, 1, max=200),
    ThingType.STIMPACK:     lambda p: add_health(p, 10),
    ThingType.MEDIKIT:      lambda p: add_health(p, 25),
    ThingType.GREEN_ARMOUR: lambda p: set_armour(p, 100, type=1),
    ThingType.SHOTGUN:      lambda p: give_weapon(p, Weapon.SHOTGUN),
    # etc.
}
```

---

### G-GS-04 — Key System (P1, S)

**What DOOM does**:
- 6 key types: blue keycard, yellow keycard, red keycard, blue skull, yellow skull, red skull.
- Carried in `player.keys: set[KeyType]`.
- Certain doors require a specific key; if the player doesn't have it: play a locked sound and show a message ("You need a blue key card to open this door.").

**Gap**: Add `keys: set` to `PlayerState`. Key pickup adds to the set. Key-locked linedef specials check the set before triggering.

---

### G-GS-05 — Power-Ups (P2, M)

**What DOOM does**: 6 power-up items that grant timed effects:

| Power-up | Effect | Duration |
|----------|--------|----------|
| Invulnerability | Immune to all damage; colourmap inverted | 30s |
| Berserk | Fist damage ×10; auto-switches to fist; restores full health | Until level end |
| Partial Invisibility | Spectre fuzz effect on player; enemies have difficulty targeting | 60s |
| Radiation Suit | Immune to floor damage | 60s |
| Computer Map | Reveals full automap | Until level end |
| Light Amplification Visor | Minimum light level raised to full brightness | 120s |

**Gap**: A `PlayerPowerups` dict of `{PowerupType: tics_remaining}`. Decremented each tic. Effect applied via condition checks in the relevant systems.

---

### G-GS-06 — Difficulty Scaling (P2, M)

**What DOOM does**: 5 difficulty levels affect:
- **Monster count**: some Thing entries are only active at certain difficulties (via Thing flags bits 0–2).
- **Damage taken by player**: `1 = ×0.5`, `2–4 = ×1.0`, `5 (Nightmare!) = ×1.0 + fast monsters`.
- **Ammo given**: on `I'm Too Young To Die`, ammo pickups give double.
- **Fast monsters (Nightmare!)**: all monster movement and attack speeds doubled; monster respawning enabled.

**Gap**: `GameSession.skill: int` (1–5) passed to `ThingSpawner` to filter Things by skill flags, and to damage calculation.

---

### G-GS-07 — Kill / Item / Secret Tracking (P2, S)

**What DOOM does**:
- `total_kills`, `total_items`, `total_secrets` — counted at level load from Things.
- `player_kills`, `player_items`, `player_secrets` — incremented as the player kills, picks up, and discovers.
- Displayed as percentages on the intermission screen.

**Gap**: Counters in `GameSession`. Increment `player_kills` when a monster dies to a player attack. Increment `player_items` on pickup. Increment `player_secrets` when the player enters a secret sector (special type 9).

---

### G-GS-08 — Teleporters (P1, M)

**What DOOM does**: Linedef special `97` (W1) or `39` (W1): when the player walks over the linedef, they are teleported to the `THING` with type `14` (teleport landing) in the sector with the matching tag. A telefog effect (smoke puff actor) is spawned at both the departure and arrival points, and a teleport sound plays.

**Gap**: Implement as a linedef special action (part of G-LVL-06):
1. Find the teleport landing Thing in the tagged sector.
2. Move player to landing position and angle.
3. Zero player momentum.
4. Spawn telefog actors at both positions.

---

### G-GS-09 — Title Screen & Demo Loop (P4, L)

**What DOOM does**: When no game is active, DOOM cycles through:
1. Title card (DOOM logo).
2. Demo playback (recorded `.LMP` demo files from the WAD).
3. Credits screen.
4. Back to title.

**Gap**: A title screen state that renders a background, cycles through a demo loop, and waits for player input to enter the main menu.

---

### G-GS-10 — Cheat Codes (P4, S)

**What DOOM does**: Typing specific key sequences during gameplay activates cheats. Classic cheats include:

| Code | Effect |
|------|--------|
| `IDDQD` | God mode (invulnerable) |
| `IDKFA` | All weapons, full ammo, all keys |
| `IDFA` | All weapons, full ammo |
| `IDSPISPOPD` / `IDCLIP` | No-clip mode |
| `IDDT` | Full automap reveal |
| `IDBEHOLDS` | Berserk |
| `IDBEHOLDI` | Invisibility |
| `IDBEHOLDV` | Invulnerability |
| `IDBEHOLDR` | Radiation suit |
| `IDBEHOLDA` | Computer map |
| `IDBEHOLDL` | Light amplification |
| `IDMYPOS` | Print player coordinates |

**Gap**: Buffer last N keypresses. On match, apply cheat effect and display confirmation message.

---

## Game Session Data

```python
@dataclass
class GameSession:
    # Level context
    episode: int = 1
    map_num: int = 1
    skill: int = 3            # 1=ITYTD, 3=HMP, 5=Nightmare

    # Player state
    player: PlayerState = field(default_factory=PlayerState)
    
    # Stats
    total_kills: int = 0
    total_items: int = 0
    total_secrets: int = 0
    player_kills: int = 0
    player_items: int = 0
    player_secrets: int = 0
    level_time: int = 0       # tics elapsed

    # Power-ups
    powerups: dict = field(default_factory=dict)
```

---

## Summary Table

| Gap | Priority | Complexity |
|-----|----------|------------|
| G-GS-01 Game state manager | P1 | S |
| G-GS-02 Thing spawning | P1 | M |
| G-GS-03 Item pickup | P1 | M |
| G-GS-04 Key system | P1 | S |
| G-GS-05 Power-ups | P2 | M |
| G-GS-06 Difficulty scaling | P2 | M |
| G-GS-07 Kill/item/secret tracking | P2 | S |
| G-GS-08 Teleporters | P1 | M |
| G-GS-09 Title screen / demo loop | P4 | L |
| G-GS-10 Cheat codes | P4 | S |
