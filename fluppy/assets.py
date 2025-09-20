"""Asset loading helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence

import pygame

from . import settings
from .entities import PipeVariant, ScrollingLayer


def _load_and_scale_background(asset_root: Path, filename: str) -> pygame.Surface:
    path = asset_root / filename
    image = pygame.image.load(str(path)).convert_alpha()
    scale = settings.SCREEN_HEIGHT / image.get_height()
    size = (int(image.get_width() * scale), int(image.get_height() * scale))
    return pygame.transform.smoothscale(image, size)


def load_background_layers(asset_root: Path) -> tuple[ScrollingLayer, List[ScrollingLayer], ScrollingLayer]:
    layers: List[ScrollingLayer] = []
    if settings.BACKGROUND_LAYERS:
        first_name, first_speed = settings.BACKGROUND_LAYERS[0]
        first_surface = _load_and_scale_background(asset_root, first_name)
        y = settings.SCREEN_HEIGHT - first_surface.get_height()
        sky_layer = ScrollingLayer(first_surface, first_speed, y)
        for image_name, speed in settings.BACKGROUND_LAYERS[1:]:
            surface = _load_and_scale_background(asset_root, image_name)
            y = settings.SCREEN_HEIGHT - surface.get_height()
            layers.append(ScrollingLayer(surface, speed, y))
    else:
        sky_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        sky_surface.fill((90, 200, 255))
        sky_layer = ScrollingLayer(sky_surface, 0)

    grass_surface = load_ground(asset_root)
    grass_layer = ScrollingLayer(
        grass_surface,
        settings.GROUND_SCROLL_SPEED,
        settings.SCREEN_HEIGHT - grass_surface.get_height(),
    )
    return sky_layer, layers, grass_layer


def load_ground(asset_root: Path) -> pygame.Surface:
    path = asset_root / settings.GRASS_IMAGE
    image = pygame.image.load(str(path)).convert_alpha()
    scale = settings.SCREEN_HEIGHT / image.get_height()
    scaled_size = (int(image.get_width() * scale), settings.SCREEN_HEIGHT)
    scaled = pygame.transform.smoothscale(image, scaled_size)
    slice_height = min(settings.GROUND_TARGET_HEIGHT, scaled.get_height())
    rect = pygame.Rect(0, scaled.get_height() - slice_height, scaled.get_width(), slice_height)
    return scaled.subsurface(rect).copy()


def load_pipe_variants(asset_root: Path) -> List[PipeVariant]:
    sheet = pygame.image.load(str(asset_root / settings.LOG_SHEET)).convert_alpha()
    variants: List[PipeVariant] = []
    target_width = 140
    for clip in settings.LOG_CLIPS:
        rect = pygame.Rect(clip)
        frame = sheet.subsurface(rect).copy()
        scale = target_width / frame.get_width()
        new_size = (target_width, int(frame.get_height() * scale))
        scaled = pygame.transform.smoothscale(frame, new_size)
        variants.append(PipeVariant(scaled, pygame.mask.from_surface(scaled)))
    return variants


def load_bird(asset_root: Path, scale: float) -> tuple[Sequence[pygame.Surface], pygame.Surface]:
    sheet = pygame.image.load(str(asset_root / settings.BIRD_SHEET)).convert_alpha()
    frames = [sheet.subsurface(pygame.Rect(clip)).copy() for clip in settings.BIRD_CLIPS]
    death_frame = frames[0]
    flap_frames = frames[1:]
    flap_frames = [
        pygame.transform.smoothscale(
            frame,
            (
                int(frame.get_width() * scale),
                int(frame.get_height() * scale),
            ),
        )
        for frame in flap_frames
    ]
    death_frame = pygame.transform.smoothscale(
        death_frame,
        (
            int(death_frame.get_width() * scale),
            int(death_frame.get_height() * scale),
        ),
    )
    return flap_frames, death_frame


def load_sounds(folder: Path) -> Dict[str, pygame.mixer.Sound]:
    sounds: Dict[str, pygame.mixer.Sound] = {}
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error:
            return sounds
    if not folder.exists():
        return sounds
    for path in folder.glob("*.wav"):
        try:
            sounds[path.stem] = pygame.mixer.Sound(str(path))
        except pygame.error:
            continue
    return sounds
