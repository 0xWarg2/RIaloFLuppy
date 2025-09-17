"""Fluppy Bird - A Pygame implementation using the provided asset pack."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import random
from typing import List, Sequence, Tuple

import pygame

SCREEN_WIDTH = 576
SCREEN_HEIGHT = 1024
FPS = 60
PIPE_SPAWN_MS = 1600
PIPE_SPEED = 220  # pixels per second
PIPE_GAP = 260
GRAVITY = 2200  # pixels per second^2
FLAP_VELOCITY = -760
MAX_DROP_SPEED = 1020
BIRD_ANIMATION_MS = 120

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
    pygame.Rect(26, 59, 213, 162),   # death frame
    pygame.Rect(26, 315, 213, 162),  # wings level
    pygame.Rect(282, 59, 213, 162),  # wings lowered
    pygame.Rect(282, 315, 213, 162), # wings lowest
]

LOG_CLIPS = [
    pygame.Rect(55, 140, 237, 1088),
    pygame.Rect(414, 140, 271, 1089),
    pygame.Rect(784, 143, 230, 1090),
    pygame.Rect(1118, 141, 247, 1088),
]

GAME_FONT_SIZE = 48
SCORE_FONT_SIZE = 72
GROUND_TARGET_HEIGHT = 160
START_FLOAT_AMPLITUDE = 8
START_FLOAT_SPEED = 2.2


class GameState(Enum):
    READY = auto()
    PLAYING = auto()
    GAME_OVER = auto()


@dataclass
class PipeVariant:
    image: pygame.Surface
    mask: pygame.Mask


class PipePair:
    def __init__(self, variants: Sequence[PipeVariant], x: float, gap_y: float, gap: int) -> None:
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

    def update(self, dt: float) -> None:
        self.x -= PIPE_SPEED * dt
        self.bottom_rect.centerx = int(self.x)
        self.top_rect.centerx = int(self.x)

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
        self.frame_timer = 0
        self.image = self.frames[0]
        self.float_offset = 0.0
        self.float_direction = 1

    def reset(self, position: Tuple[int, int]) -> None:
        self.rect = self.frames[0].get_rect(center=position)
        self.position_y = float(self.rect.centery)
        self.velocity = 0.0
        self.frame_index = 0
        self.frame_timer = 0
        self.image = self.frames[0]
        self.float_offset = 0.0
        self.float_direction = 1

    def flap(self) -> None:
        self.velocity = FLAP_VELOCITY

    def update_ready(self, dt: float, baseline_y: int) -> None:
        # Gentle floating animation while waiting to start.
        self.frame_timer += dt
        if self.frame_timer * 1000 >= BIRD_ANIMATION_MS:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.image = self.frames[self.frame_index]
        self.float_offset += START_FLOAT_SPEED * dt * self.float_direction
        if abs(self.float_offset) > START_FLOAT_AMPLITUDE:
            self.float_direction *= -1
        self.position_y = baseline_y + self.float_offset
        self.rect.centery = int(self.position_y)

    def update(self, dt: float) -> None:
        self.velocity += GRAVITY * dt
        if self.velocity > MAX_DROP_SPEED:
            self.velocity = MAX_DROP_SPEED
        self.position_y += self.velocity * dt
        self.rect.centery = int(self.position_y)
        self.frame_timer += dt
        if self.frame_timer * 1000 >= BIRD_ANIMATION_MS:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        frame = self.frames[self.frame_index]
        angle = -self.velocity * 0.06
        angle = max(-25, min(angle, 70))
        self.image = pygame.transform.rotozoom(frame, angle, 1)

    def update_falling(self, dt: float) -> None:
        self.velocity = min(self.velocity + GRAVITY * dt, MAX_DROP_SPEED)
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


class FluppyGame:
    def __init__(self, screen: pygame.Surface, asset_root: Path) -> None:
        self.screen = screen
        self.asset_root = asset_root
        self.state = GameState.READY
        self.pipe_timer = 0
        self.score = 0
        self.best_score = 0
        self.font = pygame.font.SysFont(None, GAME_FONT_SIZE)
        self.score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)

        self.sounds = self._load_sounds(asset_root.parent / "sounds")
        self.layers, self.ground = self._load_background_layers()
        self.pipe_variants = self._load_pipe_variants()
        self.bird = self._load_bird()
        self.bird_start = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.bird.reset(self.bird_start)
        self.ground_y = SCREEN_HEIGHT - self.ground.surface.get_height()
        self.pipes: List[PipePair] = []

    def _load_sounds(self, folder: Path) -> dict:
        sounds = {}
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error:
                return sounds
        for name in ["sfx_wing", "sfx_point", "sfx_hit", "sfx_die", "sfx_swooshing"]:
            path = folder / f"{name}.wav"
            if path.exists():
                sounds[name] = pygame.mixer.Sound(str(path))
        return sounds

    def _play_sound(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def _load_background_layers(self) -> Tuple[List[ScrollingLayer], ScrollingLayer]:
        layers: List[ScrollingLayer] = []
        static_surface = None
        for image_name, speed in BACKGROUND_LAYERS:
            surface = self._load_and_scale_background(image_name)
            if speed == 0:
                static_surface = surface
                continue
            y = SCREEN_HEIGHT - surface.get_height()
            layers.append(ScrollingLayer(surface, speed, y))
        if static_surface is None:
            sky_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            sky_surface.fill((90, 200, 255))
            static_layer = ScrollingLayer(sky_surface, 0)
        else:
            static_layer = ScrollingLayer(static_surface, 0, SCREEN_HEIGHT - static_surface.get_height())
        grass_surface = self._load_ground()
        grass_layer = ScrollingLayer(grass_surface, PIPE_SPEED, SCREEN_HEIGHT - grass_surface.get_height())
        self.sky = static_layer
        return layers, grass_layer

    def _load_and_scale_background(self, filename: str) -> pygame.Surface:
        path = self.asset_root / filename
        image = pygame.image.load(str(path)).convert_alpha()
        scale = max(SCREEN_WIDTH / image.get_width(), SCREEN_HEIGHT / image.get_height())
        size = (int(image.get_width() * scale), int(image.get_height() * scale))
        return pygame.transform.smoothscale(image, size)

    def _load_ground(self) -> pygame.Surface:
        path = self.asset_root / GRASS_IMAGE
        image = pygame.image.load(str(path)).convert_alpha()
        slice_height = 320
        rect = pygame.Rect(0, image.get_height() - slice_height, image.get_width(), slice_height)
        slice_surface = image.subsurface(rect).copy()
        scale = SCREEN_WIDTH / slice_surface.get_width()
        target_height = int(slice_surface.get_height() * scale)
        ground_surface = pygame.transform.smoothscale(slice_surface, (SCREEN_WIDTH, target_height))
        if ground_surface.get_height() > GROUND_TARGET_HEIGHT:
            ground_surface = pygame.transform.smoothscale(ground_surface, (SCREEN_WIDTH, GROUND_TARGET_HEIGHT))
        return ground_surface

    def _load_pipe_variants(self) -> List[PipeVariant]:
        path = self.asset_root / LOG_SHEET
        sheet = pygame.image.load(str(path)).convert_alpha()
        variants: List[PipeVariant] = []
        target_width = 140
        for rect in LOG_CLIPS:
            clip = sheet.subsurface(rect).copy()
            scale = target_width / clip.get_width()
            new_size = (target_width, int(clip.get_height() * scale))
            scaled = pygame.transform.smoothscale(clip, new_size)
            variants.append(PipeVariant(scaled, pygame.mask.from_surface(scaled)))
        return variants

    def _load_bird(self) -> Bird:
        sheet = pygame.image.load(str(self.asset_root / BIRD_SHEET)).convert_alpha()
        frames = [sheet.subsurface(rect).copy() for rect in BIRD_CLIPS]
        death_frame = frames[0]
        flap_frames = frames[1:]
        scale = 0.6
        flap_frames = [pygame.transform.smoothscale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale))) for frame in flap_frames]
        death_frame = pygame.transform.smoothscale(death_frame, (int(death_frame.get_width() * scale), int(death_frame.get_height() * scale)))
        return Bird(flap_frames, death_frame, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))

    def reset(self) -> None:
        self.state = GameState.READY
        self.score = 0
        self.pipe_timer = 0
        self.pipes.clear()
        self.bird.reset(self.bird_start)
        for layer in self.layers:
            layer.reset()
        self.ground.reset()
        self.sky.reset()

    def spawn_pipe(self) -> None:
        margin = 180
        gap_y = random.randint(margin, SCREEN_HEIGHT - self.ground.surface.get_height() - margin)
        pipe = PipePair(self.pipe_variants, SCREEN_WIDTH + 100, gap_y, PIPE_GAP)
        self.pipes.append(pipe)

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP):
            self._on_flap_request()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_flap_request()

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

    def update(self, dt: float) -> None:
        if self.state == GameState.READY:
            self.bird.update_ready(dt, self.bird_start[1])
            self._scroll_background(dt)
            return
        if self.state == GameState.PLAYING:
            self.pipe_timer += dt
            if self.pipe_timer * 1000 >= PIPE_SPAWN_MS:
                self.pipe_timer = 0
                self.spawn_pipe()
            self.bird.update(dt)
            self._scroll_background(dt)
            self._update_pipes(dt)
            self._check_collisions()
            return
        if self.state == GameState.GAME_OVER:
            self._scroll_background(dt)
            self.bird.update_falling(dt)

    def _scroll_background(self, dt: float) -> None:
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
                self.score += 1
                if self.score > self.best_score:
                    self.best_score = self.score
                self._play_sound("sfx_point")

    def _check_collisions(self) -> None:
        bird_mask = self.bird.get_mask()
        bird_rect = self.bird.rect
        if bird_rect.top <= 0:
            bird_rect.top = 0
            self.bird.velocity = 0
            self.bird.position_y = float(bird_rect.centery)
        ground_top = self.ground_y
        if bird_rect.bottom >= ground_top:
            bird_rect.bottom = ground_top
            self.bird.position_y = float(bird_rect.centery)
            self._trigger_game_over(ground_hit=True)
            return
        for pipe in self.pipes:
            if pipe.collides_with(bird_mask, bird_rect):
                self._trigger_game_over(ground_hit=False)
                return

    def _trigger_game_over(self, ground_hit: bool) -> None:
        self.state = GameState.GAME_OVER
        self._play_sound("sfx_hit")
        if ground_hit:
            self._play_sound("sfx_die")

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
            rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
            self.screen.blit(score_surface, rect)
        if self.state == GameState.READY:
            text = "Nhan SPACE hoac CLICK de bat dau"
            surface = self.font.render(text, True, (250, 250, 250))
            rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            shadow = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow, rect.move(3, 3))
            self.screen.blit(surface, rect)
        if self.state == GameState.GAME_OVER:
            lines = [
                "Thua roi!",
                f"Diem: {self.score}",
                f"Ky luc: {self.best_score}",
                "Nhan SPACE de choi lai",
            ]
            for i, line in enumerate(lines):
                surface = self.font.render(line, True, (255, 240, 240))
                rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 48))
                shadow = self.font.render(line, True, (10, 10, 10))
                self.screen.blit(shadow, rect.move(2, 2))
                self.screen.blit(surface, rect)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fluppy Bird")
    asset_root = Path(__file__).with_name("assets").joinpath("FluffyBirds-Free-Ver")
    if not asset_root.exists():
        raise FileNotFoundError(f"Khong tim thay thu muc tai san: {asset_root}")
    game = FluppyGame(screen, asset_root)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_input(event)
        game.update(dt)
        game.draw()
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
