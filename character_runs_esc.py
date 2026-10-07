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


def movement_vector(controls):
    dx, dy = horizontal_input(controls), vertical_input(controls)
    length = hypot(dx, dy)
    return (dx / length, dy / length) if length else (0.0, 0.0)


def move_character(character, dx, dy, dt):
    character.x += dx * MOVE_SPEED * dt
    character.y += dy * MOVE_SPEED * dt


def clamp_horizontal(character):
    half = CHARACTER_WIDTH / 2
    character.x = max(half, min(SCREEN_WIDTH - half, character.x))


def clamp_vertical(character):
    half = CHARACTER_HEIGHT / 2
    character.y = max(half, min(SCREEN_HEIGHT - half, character.y))


def animate(character, dt):
    interval = RUN_INTERVAL if character.state == "Run" else IDLE_INTERVAL
    character.animation_time += dt
    steps = int((character.animation_time + 1e-12) / interval)
    character.frame = (character.frame + steps) % FRAME_COUNT
    character.animation_time = max(0.0, character.animation_time - steps * interval)


ANIMATION_ROWS = {
    ("Idle", "right"): 0, ("Idle", "left"): 1,
    ("Run", "right"): 2, ("Run", "left"): 3,
}

def sprite_rectangle(character, sheet_height):
    row = ANIMATION_ROWS[character.state, character.facing]
    return (character.frame * FRAME_WIDTH,
            sheet_height - (row + 1) * FRAME_HEIGHT,
            FRAME_WIDTH, FRAME_HEIGHT)


def update(character, controls, dt):
    dx, dy = movement_vector(controls)
    update_state(character, dx, dy)
    move_character(character, dx, dy, dt)
    clamp_horizontal(character)
    clamp_vertical(character)
    animate(character, dt)


def draw(pico, background, sheet, character):
    pico.clear_canvas()
    background.draw(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                    SCREEN_WIDTH, SCREEN_HEIGHT)
    sheet.clip_draw(*sprite_rectangle(character, sheet.h),
                    character.x, character.y, CHARACTER_WIDTH, CHARACTER_HEIGHT)
    pico.update_canvas()


def handle_events(pico, controls):
    keys = {pico.SDLK_LEFT: "left", pico.SDLK_RIGHT: "right",
            pico.SDLK_UP: "up", pico.SDLK_DOWN: "down"}
    running = True
    for event in pico.get_events():
        if event.type == pico.SDL_QUIT:
            running = False
        elif event.type == pico.SDL_KEYDOWN:
            if event.key == pico.SDLK_ESCAPE:
                running = False
            elif event.key in keys:
                controls.press(keys[event.key])
        elif event.type == pico.SDL_KEYUP and event.key in keys:
            controls.release(keys[event.key])
        elif (event.type == pico.SDL_WINDOWEVENT
              and event.event == pico.SDL_WINDOWEVENT_FOCUS_LOST):
            controls.pressed.clear()
    return running


def main(smoke_test=False):
    import pico2d as pico
    background_path = asset_path("TUK_GROUND.png")
    sheet_path = asset_path("animation_sheet.png")
    pico.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    try:
        background = pico.load_image(background_path)
        sheet = pico.load_image(sheet_path)
        if background is None or sheet is None:
            raise RuntimeError("배경 또는 캐릭터 이미지를 불러오지 못했습니다.")
        if sheet.w < FRAME_COUNT * FRAME_WIDTH or sheet.h < 4 * FRAME_HEIGHT:
            raise ValueError("캐릭터 시트 크기가 8열 4행 프레임 규격보다 작습니다.")
        character, controls = Character(), Controls()
        previous = perf_counter()
        frames = 0
        while handle_events(pico, controls):
            now = perf_counter()
            dt, previous = now - previous, now
            update(character, controls, dt)
            draw(pico, background, sheet, character)
            frames += 1
            if smoke_test and frames >= 12:
                break
            pico.delay(0.01)
    finally:
        pico.close_canvas()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="방향키로 이동하고 ESC로 종료합니다.")
    parser.add_argument("--smoke-test", action="store_true",
                        help="12프레임 렌더링 후 자동 종료")
    main(parser.parse_args().smoke_test)
