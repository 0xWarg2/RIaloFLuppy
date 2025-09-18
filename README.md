# Fluppy Bird

A lightweight Flappy Bird remake written with Python and Pygame. It uses the sprites from `assets/FluffyBirds-Free-Ver` together with the sound effects in `assets/sounds`.

## Requirements

- Python 3.9 or newer
- Dependencies listed in `requirements.txt`

Recommended setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 game.py
```

 On launch you will see a difficulty picker (Easy / Normal / Hard). Use `↑/↓` or `W/S` to highlight an option and press `Enter` or `Space` to start. Press `Space` after a game over to revisit the picker. To bypass the menu entirely, set an environment variable before running, for example `FLUPPY_DIFFICULTY=hard python3 game.py`.

### macOS Bash shortcut

```bash
/bin/bash -lc 'cd /Users/xuanhaj/Dev/game/RIaloFLuppy && source .venv/bin/activate && python3 game.py'
```

## Controls

- `Space`, `↑`, or left mouse click to flap.
- When you lose, press `Space` to restart.

## Features

- Parallax background built from the layered sky, clouds, trees, and buildings.
- Four log variants (`Logs.png`) chosen at random for every pipe pair.
- The red bird sheet provides three flap frames and one defeat frame.
- Built-in scoring HUD with current score and personal best.
- Difficulty presets (Easy / Normal / Hard) that adjust pipe speed, spacing, spawn rate, bird scale, and optionally add swaying pipes.

## Tuning

Key constants live in `fluppy/settings.py`:

- `PIPE_SPEED`, `PIPE_GAP`, `PIPE_SPAWN_MS`
- `GRAVITY`, `FLAP_VELOCITY`, `MAX_DROP_SPEED`
- `SCREEN_WIDTH`, `SCREEN_HEIGHT`
- `BIRD_SCALE`
- `DIFFICULTIES` and `DIFFICULTY` for preset configuration

Edit the values and rerun `game.py` to experiment.

## Packaging

- Local build: `python -m pip install pyinstaller && python scripts/build_pyinstaller.py`. The executable lands in `dist/` together with the bundled assets.
- CI build: push a `v*` tag (or use *Run workflow* in GitHub Actions) to trigger `.github/workflows/build.yml`, which uploads platform-specific bundles.

## Project Layout

```
assets/
  FluffyBirds-Free-Ver/
  sounds/
fluppy/
  __init__.py
  __main__.py
  app.py          # FluppyGame and the main loop
  assets.py       # sprite and sound loaders
  difficulty.py   # preset resolution & helpers
  entities.py     # Bird, PipePair, scrolling background layers
  main.py         # runtime entry point (handles menu + loop)
  settings.py     # global constants and presets
  state.py        # GameState enum
game.py           # short entry that calls fluppy.main
requirements.txt
```

Feel free to add fonts or alternative assets—just update the paths if you rename anything.
