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
