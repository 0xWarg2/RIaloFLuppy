"""Enums representing overall game state."""
from __future__ import annotations

from enum import Enum, auto

class GameState(Enum):
    READY = auto()
    PLAYING = auto()
    GAME_OVER = auto()
