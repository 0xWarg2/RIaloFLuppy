"""Runtime entry for the Fluppy game."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import List

import pygame

from .app import FluppyGame
from .state import GameState
from . import settings
from .difficulty import list_difficulties


async def choose_difficulty(screen: pygame.Surface, game: FluppyGame | None = None) -> str | None:
    if os.environ.get("FLUPPY_DIFFICULTY"):
        # Environment variable already controls difficulty.
        return None

    options: List[str] = list(list_difficulties())
    if settings.DIFFICULTY in options:
        index = options.index(settings.DIFFICULTY)
    else:
        index = 0

    title_font = pygame.font.SysFont(None, 72)
    option_font = pygame.font.SysFont(None, 56)
    hint_font = pygame.font.SysFont(None, 32)
    clock = pygame.time.Clock()

    selecting = True
    while selecting:
        screen.fill((0, 0, 0))
        if game:
            game.draw()
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 30, 200))
        screen.blit(overlay, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    index = (index - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    index = (index + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    selecting = False
                elif event.key == pygame.K_ESCAPE:
                    selecting = False

        title = title_font.render("Choose Difficulty", True, (255, 240, 200))
        title_rect = title.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4))
        screen.blit(title, title_rect)

        for i, name in enumerate(options):
            label = name.capitalize()
            color = (255, 230, 120) if i == index else (200, 200, 200)
            surface = option_font.render(label, True, color)
            rect = surface.get_rect(center=(settings.SCREEN_WIDTH // 2, title_rect.bottom + 80 + i * 70))
            screen.blit(surface, rect)

        hint_text = "Press Enter/Space to start"
        surface = hint_font.render(hint_text, True, (180, 180, 200))
        rect = surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 100))
        screen.blit(surface, rect)

        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)

    settings.DIFFICULTY = options[index]
    return options[index]


def _resource_root() -> Path:
    """Return the directory that contains bundled assets.

    When packaged with tools like PyInstaller or pygbag the Python files may
    live inside an intermediate directory (e.g. `/data/data/<pkg>/assets`). We
    therefore resolve the parent directory of the package and use it as a
    search root instead of assuming the project layout.
    """

    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def _find_asset_dir(base_path: Path) -> Path:
    """Locate the sprite pack regardless of how the project was bundled."""

    candidates = (
        base_path / "assets" / "FluffyBirds-Free-Ver",
        base_path / "FluffyBirds-Free-Ver",
    )
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Asset directory not found. Looked for: "
        + ", ".join(str(path) for path in candidates)
    )


async def main_async() -> None:
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption("Fluppy Bird")

    base_path = _resource_root()
    asset_root = _find_asset_dir(base_path)
    game = FluppyGame(screen, asset_root)
    clock = pygame.time.Clock()

    selected = await choose_difficulty(screen, game)
    if selected:
        game.configure_for_difficulty()
        game.reset()

    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game.state == GameState.GAME_OVER:
                prev = settings.DIFFICULTY
                choice = await choose_difficulty(screen, game)
                if choice and choice != prev:
                    game.configure_for_difficulty()
                game.reset()
            else:
                game.handle_input(event)
        game.update(dt)
        game.draw()
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
