"""방향키 기반 캐릭터 이동 게임. python character_runs_esc.py 로 실행한다."""
from dataclasses import dataclass
from math import hypot
from pathlib import Path
from time import perf_counter


SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
CHARACTER_WIDTH = CHARACTER_HEIGHT = 100
MOVE_SPEED = 250.0
FRAME_WIDTH = FRAME_HEIGHT = 100
FRAME_COUNT = 8
IDLE_INTERVAL, RUN_INTERVAL = 0.15, 0.10
ASSET_DIRECTORY = Path(__file__).resolve().parent


def asset_path(name):
    path = ASSET_DIRECTORY / name
    if not path.is_file():
        raise FileNotFoundError(f"게임 리소스를 찾을 수 없습니다: {path}")
    return str(path)


@dataclass
class Character:
    x: float = SCREEN_WIDTH / 2
    y: float = SCREEN_HEIGHT / 2
    facing: str = "right"
    state: str = "Idle"
    frame: int = 0
    animation_time: float = 0.0


class Controls:
    def __init__(self):
        self.pressed = set()

    def press(self, direction):
        if direction in {"left", "right", "up", "down"}:
            self.pressed.add(direction)

    def release(self, direction):
        self.pressed.discard(direction)


def horizontal_input(controls):
    return int("right" in controls.pressed) - int("left" in controls.pressed)


def vertical_input(controls):
    return int("up" in controls.pressed) - int("down" in controls.pressed)


def update_facing(character, dx):
    if dx:
        character.facing = "right" if dx > 0 else "left"


def update_state(character, dx, dy):
    previous = character.state, character.facing
    update_facing(character, dx)
    character.state = "Run" if dx or dy else "Idle"
    if previous != (character.state, character.facing):
        character.frame = 0
        character.animation_time = 0.0
