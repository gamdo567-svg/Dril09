from pathlib import Path
from pico2d import *


open_canvas()
grass = load_image( 'grass.png')
character = load_image('animation_sheet.png')

# fill here
running = True
dir = 0
x = 800 // 2
frame = 0

def handle_events():
    global running, dir, x
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                dir += 1
            elif event.key == SDLK_LEFT:
                dir -= 1
            elif event.key == SDLK_ESCAPE:
                running = False
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                dir -= 1
            elif event.key == SDLK_LEFT:
                dir += 1

while running:
    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame*100,100,100,100,x,90)
    update_canvas()
    handle_events()
    x += dir * 5
    frame = (frame + 1) % 8
    delay(0.05)

close_canvas()
