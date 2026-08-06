# Gap: Audio

## What DOOM Does

DOOM has two audio subsystems: **sound effects** (digitised PCM samples) and **music** (OPL2 FM synthesis or MIDI, depending on hardware). Both are critical to the DOOM experience.

---

## Current State

No audio system exists. The game runs in silence.

---

## Gaps

### G-AUD-01 — Sound Effect Playback (P1, M)

**What DOOM does**:
- Up to 8 simultaneous sound channels.
- Each channel plays one digitised sound (8-bit 11 kHz PCM in the original WAD).
- Sounds are referenced by name (e.g., `DSPISTOL`, `DSSHOTGN`, `DSITEMUP`).
- Stored in the WAD as `DS*` lumps.

**Gap**: Integrate Raylib's audio system (`InitAudioDevice`, `LoadSound`, `PlaySound`) or a library like `pygame.mixer` or `sounddevice`.

**Implementation notes**:
- Raylib already supports audio natively: `ray.init_audio_device()`, `ray.load_sound()`, `ray.play_sound()`.
- WAD sounds need to be extracted from the `DS*` lumps and converted to WAV/OGG for playback.
- Alternatively, use freely licensed DOOM-compatible sound replacements (Creative Commons).
- Key sounds needed for gameplay: weapon fires (×9), monster sees player, monster dies (×9), item pickup, door open/close, player pain/death, level exit.
- Channel management: track which of the 8 channels is playing, pre-empt lowest-priority channel when all are busy.

**Priority system**: each sound has a priority value (0–255). When all channels are full, the lowest-priority sound is stopped for the new one.

```python
class SoundSystem:
    MAX_CHANNELS = 8
    def play(self, sound_name: str, priority: int, origin: Actor = None): ...
    def update(self): ...  # called each tic to update positions
```

---

### G-AUD-02 — Positional / Panned Audio (P2, M)

**What DOOM does**:
- Sounds have an `origin` actor or map position.
- Volume scales with distance from player: `vol = 255 - (distance / MAX_SOUND_DIST) * 255`.
- Panning: the angle from the player's facing to the sound origin determines left/right pan.
- Max distance: ~1200 map units beyond which sounds are inaudible.

**Gap**: For each playing channel, compute distance and angle to the player's position. Apply volume and pan to the Raylib sound channel.

**Implementation notes**:
- Raylib's `SetSoundVolume(sound, vol)` and `SetSoundPan(sound, pan)` control per-sound attributes.
- `pan = 0.0` = full left, `0.5` = centre, `1.0` = full right.
- Compute pan from the signed cross-product of player forward and (origin - player_pos).

---

### G-AUD-03 — Music Playback (P2, M)

**What DOOM does**:
- Each level has an associated music track from the DOOM WAD (e.g., E1M1 → `D_E1M1`).
- Music is stored as MUS format (a compact MIDI variant) in the WAD.
- On hardware it played through OPL2 FM synthesis (Sound Blaster / AdLib).
- Source ports typically convert MUS → MIDI and play via the OS MIDI synth.

**Gap**: Music playback with level-specific tracks.

**Implementation notes**:
- **Easiest approach**: Use freely licensed OGG/MP3 conversions of the DOOM soundtrack (many exist under various licences). Raylib can play OGG with `LoadMusicStream` / `PlayMusicStream`.
- **Authentic approach**: Parse MUS format and output MIDI events, play via `fluidsynth` or `pygame.midi`.
- **OPL emulation** (P4): Use an OPL2 emulator library (e.g., `nuked-opl3`) for bit-accurate FM synthesis — significant complexity.
- Music must loop seamlessly. Raylib's music streaming with `UpdateMusicStream()` per frame handles this.

```python
class MusicSystem:
    def play_level_music(self, level: str): ...  # e.g., "E1M1"
    def update(self): ...  # called each frame
    def stop(self): ...
```

---

### G-AUD-04 — Sound Priority System (P3, S)

**What DOOM does**:
- Each sound definition has a `priority` (0–255). Higher = more important.
- When all 8 channels are occupied, the new sound evicts the lowest-priority active sound.
- If the new sound has lower priority than all active sounds, it is dropped silently.

**Gap**: Add priority comparison logic to `SoundSystem.play()`.

---

### G-AUD-05 — Distance Attenuation (P2, S)

See G-AUD-02; this is the volume part of positional audio.

Key constants:
- `S_CLIPPING_DIST = 1200` — beyond this, no sound.
- `S_CLOSE_DIST = 160` — within this, full volume.
- Linear interpolation between the two.

---

### G-AUD-06 — Player Sound Feedback (P1, S)

**What DOOM does**:
- Player has their own sound events: pain grunt (on damage), death scream, item pickup jingle.
- Player pain sounds use a random index: `DSPLPAIN` (one sound in vanilla, slight variation).
- Weapon sounds are played at the player's position (always full volume, centre pan).

**Gap**: Hook sound playback into player damage, death, and item pickup events.

---

## Key Sound Events Mapping

| Event | Sound Lump | Priority |
|-------|-----------|----------|
| Pistol fire | `DSPISTOL` | 64 |
| Shotgun fire | `DSSHOTGN` | 64 |
| Chaingun fire | `DSPISTOL` | 64 |
| Rocket launch | `DSRLAUNC` | 64 |
| Rocket explode | `DSBAREXP` | 77 |
| BFG fire | `DSBFG` | 64 |
| Player pain | `DSPLPAIN` | 96 |
| Player death | `DSPLDETH` | 96 |
| Item pickup | `DSITEMUP` | 78 |
| Weapon pickup | `DSWPNUP` | 78 |
| Imp alert | `DSBGSIT1/2` | 98 |
| Imp death | `DSBGDTH1/2` | 20 |
| Imp attack | `DSFIRSHT` | 70 |
| Door open | `DSDOROPN` | 61 |
| Door close | `DSDORCLS` | 61 |
| Switch | `DSSWTCHN` | 78 |
| Teleport | `DSTELEPT` | 78 |

---

## Summary Table

| Gap | Priority | Complexity |
|-----|----------|------------|
| G-AUD-01 Sound effect playback | P1 | M |
| G-AUD-02 Positional audio | P2 | M |
| G-AUD-03 Music playback | P2 | M |
| G-AUD-04 Sound priority system | P3 | S |
| G-AUD-05 Distance attenuation | P2 | S |
| G-AUD-06 Player sound feedback | P1 | S |
