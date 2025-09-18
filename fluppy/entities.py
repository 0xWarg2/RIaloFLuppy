"""Entity classes used across game phases."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple

import pygame

from . import settings


@dataclass
class PipeVariant:
    image: pygame.Surface
    mask: pygame.Mask


class PipePair:
    """Scrolling pipe pair reused in Phase 1."""

    def __init__(
        self,
        variants: Sequence[PipeVariant],
        x: float,
        gap_y: float,
        gap: int,
        sway_amplitude: int = 0,
        sway_speed: float = 0.0,
    ) -> None:
        bottom_variant = random.choice(variants)
        top_variant = random.choice(variants)
        self.bottom_image = bottom_variant.image
        self.bottom_mask = bottom_variant.mask
        self.top_image = pygame.transform.flip(top_variant.image, False, True)
        self.top_mask = pygame.mask.from_surface(self.top_image)
        self.bottom_rect = self.bottom_image.get_rect(midtop=(x, gap_y + gap / 2))
        self.top_rect = self.top_image.get_rect(midbottom=(x, gap_y - gap / 2))
        self.x = float(self.bottom_rect.centerx)
        self.passed = False
        self.sway_amplitude = sway_amplitude
        self.sway_speed = sway_speed
        self.base_gap_center = gap_y
        self.time = 0.0

    def update(self, dt: float) -> None:
        self.x -= settings.PIPE_SPEED * dt
        self.bottom_rect.centerx = int(self.x)
        self.top_rect.centerx = int(self.x)
        if self.sway_amplitude and self.sway_speed:
            self.time += dt * self.sway_speed
            offset = math.sin(self.time) * self.sway_amplitude
            center = self.base_gap_center + offset
            half_gap = settings.PIPE_GAP / 2
            self.bottom_rect.midtop = (int(self.x), int(center + half_gap))
            self.top_rect.midbottom = (int(self.x), int(center - half_gap))

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.top_image, self.top_rect)
        surface.blit(self.bottom_image, self.bottom_rect)

    def is_offscreen(self) -> bool:
        return self.bottom_rect.right < -10

    def collides_with(self, bird_mask: pygame.Mask, bird_rect: pygame.Rect) -> bool:
        top_offset = (self.top_rect.x - bird_rect.x, self.top_rect.y - bird_rect.y)
        bottom_offset = (self.bottom_rect.x - bird_rect.x, self.bottom_rect.y - bird_rect.y)
        if bird_mask.overlap(self.top_mask, top_offset):
            return True
        if bird_mask.overlap(self.bottom_mask, bottom_offset):
            return True
        return False


class Bird:
    """Player-controlled bird from Phase 1."""

    def __init__(
        self,
        frames: Sequence[pygame.Surface],
        death_frame: pygame.Surface,
        start_position: Tuple[int, int],
    ) -> None:
        self.frames = list(frames)
        self.death_frame = death_frame
        self.rect = self.frames[0].get_rect(center=start_position)
        self.position_y = float(self.rect.centery)
        self.velocity = 0.0
        self.frame_index = 0
        self.frame_timer = 0.0
        self.image = self.frames[0]
        self.float_offset = 0.0
        self.float_direction = 1

    def reset(self, position: Tuple[int, int]) -> None:
        self.rect = self.frames[0].get_rect(center=position)
        self.position_y = float(self.rect.centery)
        self.velocity = 0.0
        self.frame_index = 0
        self.frame_timer = 0.0
        self.image = self.frames[0]
        self.float_offset = 0.0
        self.float_direction = 1

    def flap(self) -> None:
        self.velocity = settings.FLAP_VELOCITY

    def update_ready(self, dt: float, baseline_y: int) -> None:
        self.frame_timer += dt
        if self.frame_timer * 1000 >= settings.BIRD_ANIMATION_MS:
            self.frame_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.image = self.frames[self.frame_index]
        self.float_offset += settings.START_FLOAT_SPEED * dt * self.float_direction
        if abs(self.float_offset) > settings.START_FLOAT_AMPLITUDE:
            self.float_direction *= -1
        self.position_y = baseline_y + self.float_offset
        self.rect.centery = int(self.position_y)

    def update(self, dt: float) -> None:
        self.velocity += settings.GRAVITY * dt
        if self.velocity > settings.MAX_DROP_SPEED:
            self.velocity = settings.MAX_DROP_SPEED
        self.position_y += self.velocity * dt
        self.rect.centery = int(self.position_y)
        self.frame_timer += dt
        if self.frame_timer * 1000 >= settings.BIRD_ANIMATION_MS:
            self.frame_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        frame = self.frames[self.frame_index]
        angle = -self.velocity * 0.06
        angle = max(-25, min(angle, 70))
        self.image = pygame.transform.rotozoom(frame, angle, 1)

    def update_falling(self, dt: float) -> None:
        self.velocity = min(self.velocity + settings.GRAVITY * dt, settings.MAX_DROP_SPEED)
        self.position_y += self.velocity * dt
        self.rect.centery = int(self.position_y)
        self.image = pygame.transform.rotozoom(self.death_frame, 70, 1)

    def get_mask(self) -> pygame.Mask:
        return pygame.mask.from_surface(self.image)


class ScrollingLayer:
    def __init__(self, surface: pygame.Surface, speed: float, y: int = 0) -> None:
        self.surface = surface
        self.speed = speed
        self.y = y
        self.width = surface.get_width()
        self.positions = [0.0, float(self.width)]

    def reset(self) -> None:
        self.positions = [0.0, float(self.width)]

    def update(self, dt: float) -> None:
        if self.speed == 0:
            return
        distance = self.speed * dt
        for i in range(2):
            self.positions[i] -= distance
        for i in range(2):
            if self.positions[i] <= -self.width:
                other = 1 - i
                self.positions[i] = self.positions[other] + self.width

    def draw(self, surface: pygame.Surface) -> None:
        for x in self.positions:
            surface.blit(self.surface, (int(x), self.y))
