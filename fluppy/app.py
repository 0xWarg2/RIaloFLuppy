"""Core game application for the classic Fluppy phase."""
from __future__ import annotations

import random
from pathlib import Path
from typing import List

import pygame

from . import assets, settings
from .difficulty import apply_difficulty
from .entities import Bird, PipePair, ScrollingLayer
from .state import GameState


class FluppyGame:
    def __init__(self, screen: pygame.Surface, asset_root: Path) -> None:
        self.screen = screen
        self.asset_root = asset_root
        self.state = GameState.READY
        self.pipe_timer = 0.0
        self.score = 0
        self.best_score = 0
        self.font = pygame.font.SysFont(None, settings.GAME_FONT_SIZE)
        self.score_font = pygame.font.SysFont(None, settings.SCORE_FONT_SIZE)

        self.sounds = assets.load_sounds(asset_root.parent / "sounds")
        self._music_channel = None
        self._start_music()
        self.sky, self.layers, self.ground = assets.load_background_layers(asset_root)
        self.pipe_variants = assets.load_pipe_variants(asset_root)

        self.configure_for_difficulty()

        self.ground_y = settings.SCREEN_HEIGHT - self.ground.surface.get_height()
        self.pipes: List[PipePair] = []
        self.reset(keep_best=True)

    # ------------------------------------------------------------------
    # Audio helper
    def _play_sound(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def _start_music(self) -> None:
        music = self.sounds.get("backgroundmusic")
        if not music:
            return
        music.set_volume(settings.MUSIC_VOLUME)
        channel = getattr(self, "_music_channel", None)
        if channel and channel.get_busy():
            return
        self._music_channel = music.play(loops=-1)
        if self._music_channel:
            self._music_channel.set_volume(settings.MUSIC_VOLUME)

    # ------------------------------------------------------------------
    # Lifecycle
    def configure_for_difficulty(self) -> None:
        sway_amplitude, sway_speed = apply_difficulty()
        self.sway_amplitude = sway_amplitude
        self.sway_speed = sway_speed
        bird_frames, death_frame = assets.load_bird(self.asset_root, settings.BIRD_SCALE)
        start_pos = (settings.SCREEN_WIDTH // 4, settings.SCREEN_HEIGHT // 2)
        self.bird = Bird(bird_frames, death_frame, start_pos)
        self.bird_start = start_pos

    def reset(self, *, keep_best: bool = True) -> None:
        self.state = GameState.READY
        if not keep_best:
            self.best_score = 0
        self.score = 0
        self.pipe_timer = 0.0
        self.pipes.clear()
        self.bird.reset(self.bird_start)
        self.sky.reset()
        for layer in self.layers:
            layer.reset()
        self.ground.reset()

    def spawn_pipe(self) -> None:
        top_margin = 180
        ground_top = settings.SCREEN_HEIGHT - self.ground.surface.get_height()
        min_center = max(top_margin, settings.PIPE_GAP // 2)
        max_center = ground_top - settings.PIPE_GAP // 2
        gap_y = random.randint(min_center, max_center)
        pipe = PipePair(
            self.pipe_variants,
            settings.SCREEN_WIDTH + 100,
            gap_y,
            settings.PIPE_GAP,
            min_center,
            max_center,
            sway_amplitude=self.sway_amplitude,
            sway_speed=self.sway_speed,
        )
        self.pipes.append(pipe)

    # ------------------------------------------------------------------
    # Input handling
    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP):
            self._on_flap_request()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_flap_request()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _on_flap_request(self) -> None:
        if self.state == GameState.READY:
            self.state = GameState.PLAYING
            self.bird.flap()
            self._play_sound("sfx_swooshing")
        elif self.state == GameState.PLAYING:
            self.bird.flap()
            self._play_sound("sfx_wing")
        elif self.state == GameState.GAME_OVER:
            self.reset()

    # ------------------------------------------------------------------
    # Update loop
    def update(self, dt: float) -> None:
        if self.state == GameState.READY:
            self.bird.update_ready(dt, self.bird_start[1])
            self._scroll_background(dt)
            return
        if self.state == GameState.PLAYING:
            self._update_play(dt)
            return
        if self.state == GameState.GAME_OVER:
            self._scroll_background(dt)
            self.bird.update_falling(dt)

    def _update_play(self, dt: float) -> None:
        self.pipe_timer += dt
        if self.pipe_timer * 1000 >= settings.PIPE_SPAWN_MS:
            self.pipe_timer = 0.0
            self.spawn_pipe()
        self.bird.update(dt)
        self._scroll_background(dt)
        self._update_pipes(dt)
        self._check_collisions()

    def _scroll_background(self, dt: float) -> None:
        self.sky.update(dt)
        for layer in self.layers:
            layer.update(dt)
        self.ground.update(dt)

    def _update_pipes(self, dt: float) -> None:
        for pipe in list(self.pipes):
            pipe.update(dt)
            if pipe.is_offscreen():
                self.pipes.remove(pipe)
                continue
            if not pipe.passed and pipe.top_rect.centerx < self.bird.rect.centerx:
                pipe.passed = True
                self._increment_score(1)
                self._play_sound("sfx_point")

    def _increment_score(self, amount: int) -> None:
        self.score += amount
        if self.score > self.best_score:
            self.best_score = self.score

    def _check_collisions(self) -> None:
        bird_mask = self.bird.get_mask()
        bird_rect = self.bird.rect
        if bird_rect.top <= 0:
            bird_rect.top = 0
            self.bird.velocity = 0
            self.bird.position_y = float(bird_rect.centery)
            self._trigger_game_over(False)
            return
        ground_top = self.ground_y
        if bird_rect.bottom >= ground_top:
            bird_rect.bottom = ground_top
            self.bird.position_y = float(bird_rect.centery)
            self._trigger_game_over(True)
            return
        for pipe in self.pipes:
            if pipe.collides_with(bird_mask, bird_rect):
                self._trigger_game_over(False)
                return

    def _trigger_game_over(self, ground_hit: bool) -> None:
        self.state = GameState.GAME_OVER
        self._play_sound("sfx_hit")
        if ground_hit:
            self._play_sound("sfx_die")

    # ------------------------------------------------------------------
    # Rendering
    def draw(self) -> None:
        self.sky.draw(self.screen)
        for layer in self.layers:
            layer.draw(self.screen)
        for pipe in self.pipes:
            pipe.draw(self.screen)
        self.screen.blit(self.bird.image, self.bird.rect)
        self.ground.draw(self.screen)
        self._draw_hud()

    def _draw_hud(self) -> None:
        if self.state in (GameState.PLAYING, GameState.GAME_OVER) and self.score:
            score_surface = self.score_font.render(str(self.score), True, (255, 255, 255))
            rect = score_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, 120))
            self.screen.blit(score_surface, rect)
        if self.state == GameState.READY:
            text = "Press SPACE or CLICK to start"
            surface = self.font.render(text, True, (250, 250, 250))
            rect = surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3))
            shadow = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow, rect.move(3, 3))
            self.screen.blit(surface, rect)
        if self.state == GameState.GAME_OVER:
            lines = [
                "Game Over!",
                f"Score: {self.score}",
                f"Best: {self.best_score}",
                "Press SPACE to play again",
            ]
            for i, line in enumerate(lines):
                surface = self.font.render(line, True, (255, 240, 240))
                rect = surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + i * 48))
                shadow = self.font.render(line, True, (10, 10, 10))
                self.screen.blit(shadow, rect.move(2, 2))
                self.screen.blit(surface, rect)
