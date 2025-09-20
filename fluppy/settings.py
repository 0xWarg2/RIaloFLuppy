"""Game-wide constant settings."""

from dataclasses import dataclass
from typing import Dict

SCREEN_WIDTH = 576
SCREEN_HEIGHT = 1024
FPS = 60
PIPE_SPAWN_MS = 1600
PIPE_SPEED = 220
PIPE_GAP = 260
GRAVITY = 2200
FLAP_VELOCITY = -760
MAX_DROP_SPEED = 1020
BIRD_ANIMATION_MS = 120
BIRD_SCALE = 0.187
GROUND_SCROLL_SPEED = 60

BACKGROUND_LAYERS = [
    ("Buildingsfull.png", 60),
]

GRASS_IMAGE = "Buildingsfull.png"
LOG_SHEET = "Logs.png"
BIRD_SHEET = "Red_Bird2.png"

BIRD_CLIPS = [
    (56, 127, 512, 457),
    (56, 735, 512, 457),
    (648, 127, 512, 457),
    (648, 735, 504, 457),
]

LOG_CLIPS = [
    (55, 140, 237, 1088),
    (414, 140, 271, 1089),
    (784, 143, 230, 1090),
    (1118, 141, 247, 1088),
]

GAME_FONT_SIZE = 48
SCORE_FONT_SIZE = 72
GROUND_TARGET_HEIGHT = 50
START_FLOAT_AMPLITUDE = 8
START_FLOAT_SPEED = 2.2
MUSIC_VOLUME = 0.4


@dataclass(frozen=True)
class DifficultyPreset:
    pipe_speed: int
    pipe_gap: int
    pipe_spawn_ms: int
    bird_scale: float
    pipe_sway: bool = False
    sway_amplitude: int = 0
    sway_speed: float = 0.0


DIFFICULTIES: Dict[str, DifficultyPreset] = {
    "easy": DifficultyPreset(pipe_speed=180, pipe_gap=320, pipe_spawn_ms=1750, bird_scale=0.166),
    "normal": DifficultyPreset(pipe_speed=220, pipe_gap=260, pipe_spawn_ms=1600, bird_scale=0.187),
    "hard": DifficultyPreset(
        pipe_speed=260,
        pipe_gap=220,
        pipe_spawn_ms=1450,
        bird_scale=0.208,
        pipe_sway=True,
        sway_amplitude=40,
        sway_speed=2.2,
    ),
}

DIFFICULTY = "normal"
