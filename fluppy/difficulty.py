"""Difficulty helpers for tuning gameplay parameters."""
from __future__ import annotations

import os
from typing import Iterable, Tuple

from . import settings

_ORDERED_DIFFICULTIES = list(settings.DIFFICULTIES.keys())


def list_difficulties() -> Iterable[str]:
    return _ORDERED_DIFFICULTIES


def normalize(name: str) -> str | None:
    key = name.lower()
    if key in settings.DIFFICULTIES:
        return key
    return None


def resolve_difficulty() -> settings.DifficultyPreset:
    env_choice = os.environ.get("FLUPPY_DIFFICULTY")
    if env_choice:
        normalized = normalize(env_choice)
        if normalized:
            settings.DIFFICULTY = normalized
            return settings.DIFFICULTIES[normalized]
    if settings.DIFFICULTY not in settings.DIFFICULTIES:
        settings.DIFFICULTY = _ORDERED_DIFFICULTIES[0]
    return settings.DIFFICULTIES[settings.DIFFICULTY]


def apply_difficulty() -> Tuple[int, float]:
    preset = resolve_difficulty()
    settings.PIPE_SPEED = preset.pipe_speed
    settings.PIPE_GAP = preset.pipe_gap
    settings.PIPE_SPAWN_MS = preset.pipe_spawn_ms
    settings.BIRD_SCALE = preset.bird_scale
    sway_speed = preset.sway_speed if preset.pipe_sway else 0.0
    amplitude = preset.sway_amplitude if preset.pipe_sway else 0
    return amplitude, sway_speed
