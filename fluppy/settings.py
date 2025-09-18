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
BIRD_SCALE = 0.45

BACKGROUND_LAYERS = [
    ("Sky.png", 0),
    ("Clouds.png", 12),
    ("Trees.png", 30),
    ("Buildings.png", 60),
]

GRASS_IMAGE = "Grass.png"
LOG_SHEET = "Logs.png"
BIRD_SHEET = "Red_Bird.png"

BIRD_CLIPS = [
    (26, 59, 213, 162),
    (26, 315, 213, 162),
    (282, 59, 213, 162),
    (282, 315, 213, 162),
]

LOG_CLIPS = [
    (55, 140, 237, 1088),
    (414, 140, 271, 1089),
    (784, 143, 230, 1090),
    (1118, 141, 247, 1088),
]

GAME_FONT_SIZE = 48
SCORE_FONT_SIZE = 72
GROUND_TARGET_HEIGHT = 160
START_FLOAT_AMPLITUDE = 8
START_FLOAT_SPEED = 2.2


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
    "easy": DifficultyPreset(pipe_speed=180, pipe_gap=320, pipe_spawn_ms=1750, bird_scale=0.4),
    "normal": DifficultyPreset(pipe_speed=220, pipe_gap=260, pipe_spawn_ms=1600, bird_scale=0.45),
    "hard": DifficultyPreset(
        pipe_speed=260,
        pipe_gap=220,
        pipe_spawn_ms=1450,
        bird_scale=0.5,
        pipe_sway=True,
        sway_amplitude=40,
        sway_speed=2.2,
    ),
}

DIFFICULTY = "normal"
