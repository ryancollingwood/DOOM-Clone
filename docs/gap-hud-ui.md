# Gap: HUD & UI

## What DOOM Does

DOOM's UI is minimal and iconic: a status bar at the bottom of the screen showing health, ammo, armour, and a face portrait, plus menus for game management. All UI is drawn in 2D screen space after the 3D render.

---

## Current State

| Feature | Status |
|---------|--------|
| FPS counter | Implemented (Raylib default) |
| 2D minimap overlay | Implemented |
| Status bar | Not implemented |
| Main menu | Not implemented |
| Pause menu | Not implemented |
| HUD messages | Not implemented |
| Intermission screen | Not implemented |
| Save / load | Not implemented |
| Options menu | Not implemented |

---

## Gaps

### G-HUD-01 — Status Bar (P1, M)

**What DOOM does**: The status bar occupies the bottom 40px of the 200px game viewport (200×168 for 3D, 200×32 for status bar). It contains:

| Element | Position | Content |
|---------|----------|---------|
| Ammo count | Left | Current ammo for active weapon (3-digit number) |
| Health % | Centre-left | Player health (3-digit number, red if < 20) |
| Arms | Centre | 2×3 grid of weapon slot indicators (lit if owned) |
| Face | Centre | Doomguy face — reacts to damage direction, health level |
| Armour % | Centre-right | Armour percentage |
| Key icons | Right-centre | Blue/yellow/red key and skull icons |
| Ammo counts | Far right | 4 current/max ammo pairs (bullets/shells/cells/rockets) |

**DOOM status bar sprite**: `STBAR` (320×32 pixel bitmap). Numbers use the `STTNUM*` and `STGNUM*` sprite patches. Face uses `STFST*` (facing direction × damage level × expression).

**Implementation notes**:
- In Raylib: after `EndMode3D()`, render a 320×32 panel at the bottom of the window.
- Use `DrawTextureRec()` to composite sprite patches at known offsets.
- For a custom art-free version: use Raylib's `DrawText()` with coloured rectangles as placeholders until proper sprite assets are available.
- The **face** is complex: 5 health levels × 3 direction-of-damage frames × 5 expressions (normal, ouch, evil grin on pickup, dead). Simplify initially to a static face or a single colour indicator.

---

### G-HUD-02 — In-Game Messages (P2, S)

**What DOOM does**: Text messages appear at the top-left of the screen for ~4 seconds (140 tics):
- Item pickup: "Picked up a health bonus.", "You got the shotgun!", etc.
- Secret found: "You found a secret area!"
- Switches: some doors/switches print confirmatory text.

**Gap**: A message queue with timed display.

```python
class MessageDisplay:
    def post(self, text: str, tics: int = 140): ...
    def update(self): ...        # decrement tic counter, pop expired
    def draw(self, screen): ...  # DrawText at top-left if active
```

---

### G-HUD-03 — Main Menu (P1, M)

**What DOOM does**:
- ESC (from title screen) opens main menu.
- Options: New Game, Options, Load Game, Save Game, Read This! (help), Quit Game.
- Skull cursor selects items; Enter/Fire confirms, ESC backs out.
- Animated flame/Doom logo at top.

**Gap**: A menu state machine that:
1. Replaces the game view with a menu background when active.
2. Handles arrow-key navigation and Enter/Escape.
3. Triggers appropriate actions (start game, quit, etc.).

**Implementation notes**:
- Represent menus as a stack of `Menu` objects, each with a list of `MenuItem(label, action)`.
- Push/pop the menu stack on ESC / Enter.
- For art-free mode: render as coloured rectangles + Raylib text.

---

### G-HUD-04 — Episode & Skill Selection (P1, S)

**What DOOM does**:
- New Game → Episode select (Knee-Deep, Shores of Hell, Inferno, Thy Flesh Consumed).
- Then Skill select (I'm Too Young to Die, Hey Not Too Rough, Hurt Me Plenty, Ultra-Violence, Nightmare!).
- Skill affects monster count, damage taken, and ammo availability.

**Gap**: Two sub-menu screens feeding into level loading with the selected parameters.

---

### G-HUD-05 — Pause Menu (P1, S)

**What DOOM does**: Pressing ESC during play brings up the main menu (DOOM pauses the game). The game is fully paused (tic counter stops).

**Gap**: On ESC key press during gameplay:
- Set `game_state = PAUSED`.
- Stop all game tic updates.
- Render the 3D frame underneath, overlay the main menu.
- Resume on ESC / selecting "Continue".

---

### G-HUD-06 — Intermission Screen (P2, M)

**What DOOM does**: After reaching the exit, the intermission ("You are here") screen shows:
- Par time (design time) vs actual time.
- Kills: `xx%` of total.
- Items: `xx%` of total.
- Secrets: `xx%` of total.
- Animated level map with "You are here" pin and path to next level.
- Tab or Fire to advance.

**Gap**: A `GameState.INTERMISSION` state that:
- Records kill/item/secret counts.
- Displays them with a count-up animation.
- Transitions to the next level or episode end screen.

---

### G-HUD-07 — Weapon Slot Indicator (P1, S)

Part of the status bar (G-HUD-01). The "ARMS" box shows weapon slots 2–7 lit (yellow) when owned.

**Gap**: Integrate `player.weapons_owned` set with the status bar render.

---

### G-HUD-08 — Key Inventory Display (P2, S)

Part of the status bar. Shows skull/key icons for each of the 6 key types carried.

**Gap**: Integrate `player.keys` set with status bar render. Icons: `STKEYS0`–`STKEYS5`.

---

### G-HUD-09 — Save & Load Game (P3, L)

**What DOOM does**: 6 save slots with custom names. Saves serialise the full game state: level, player position, health, ammo, weapons, monster states, door states, switches, etc.

**Gap**: A serialisation system for `GameState`. In Python, `pickle` or `json` can handle this. Key challenge: monster and sector state must all be captured correctly.

---

### G-HUD-10 — Options Menu (P3, M)

**What DOOM does**: Controls screen size, mouse sensitivity, music/sound volume, always-run toggle, mouse invert.

**Gap**: An options menu that modifies values in `settings.py` or a runtime `Config` object, with persistence to disk.

---

### G-HUD-11 — Automap Full-Screen Mode (P3, M)

See gap-rendering.md G-REN-08. In DOOM, the automap is toggled with Tab and takes over the full screen. It is distinct from the minimap overlay currently implemented.

---

## UI State Machine

```
TITLE_SCREEN
     ↓ ESC / any key
MAIN_MENU
     ├── New Game → EPISODE_SELECT → SKILL_SELECT → LOADING → PLAYING
     ├── Load Game → LOAD_MENU → LOADING → PLAYING
     ├── Save Game (during PLAYING) → SAVE_MENU → PLAYING
     ├── Options → OPTIONS_MENU → back
     └── Quit → QUIT_CONFIRM → exit()

PLAYING
     ├── ESC → MAIN_MENU (paused)
     ├── Tab → AUTOMAP_OVERLAY (not paused)
     ├── Reach exit → INTERMISSION → next level or TITLE_SCREEN
     └── Player dies → DEATH_SCREEN → PLAYING (restart) or MAIN_MENU
```

---

## Summary Table

| Gap | Priority | Complexity |
|-----|----------|------------|
| G-HUD-01 Status bar | P1 | M |
| G-HUD-02 In-game messages | P2 | S |
| G-HUD-03 Main menu | P1 | M |
| G-HUD-04 Episode / skill select | P1 | S |
| G-HUD-05 Pause menu | P1 | S |
| G-HUD-06 Intermission screen | P2 | M |
| G-HUD-07 Weapon slot indicator | P1 | S |
| G-HUD-08 Key inventory display | P2 | S |
| G-HUD-09 Save / load game | P3 | L |
| G-HUD-10 Options menu | P3 | M |
| G-HUD-11 Automap full-screen | P3 | M |
