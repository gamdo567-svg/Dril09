"""PRD의 이동, 상태, 경계 및 이벤트 규칙 회귀 검증."""
import unittest
from math import hypot
from types import SimpleNamespace
import character_runs_esc as game


class GameTests(unittest.TestCase):
    def test_four_directions_and_release(self):
        for key, expected in [('right', (525, 400)), ('left', (475, 400)),
                              ('up', (500, 425)), ('down', (500, 375))]:
            with self.subTest(key=key):
                c, keys = game.Character(), game.Controls()
                keys.press(key)
                keys.press(key)  # OS 키 반복은 속도를 증가시키지 않는다.
                game.update(c, keys, .1)
                self.assertEqual((c.x, c.y), expected)
                self.assertEqual(c.state, 'Run')
                keys.release(key)
                game.update(c, keys, .1)
                self.assertEqual((c.x, c.y), expected)
                self.assertEqual(c.state, 'Idle')

    def test_all_diagonals_have_same_speed(self):
        for horizontal in ('left', 'right'):
            for vertical in ('up', 'down'):
                c, keys = game.Character(), game.Controls()
                keys.press(horizontal)
                keys.press(vertical)
                game.update(c, keys, .1)
                self.assertAlmostEqual(hypot(c.x - 500, c.y - 400), 25)
                self.assertEqual(c.facing, horizontal)

    def test_vertical_and_idle_preserve_facing(self):
        for facing in ('left', 'right'):
            c, keys = game.Character(), game.Controls()
            keys.press(facing)
            game.update(c, keys, .01)
            keys.release(facing)
            for vertical in ('up', 'down'):
                keys.press(vertical)
                game.update(c, keys, .01)
                self.assertEqual(c.facing, facing)
                keys.release(vertical)
            game.update(c, keys, .01)
            self.assertEqual((c.state, c.facing), ('Idle', facing))

    def test_opposites_cancel_and_partial_release(self):
        c, keys = game.Character(), game.Controls()
        for key in ('left', 'right', 'up', 'down'):
            keys.press(key)
        game.update(c, keys, .1)
        self.assertEqual((c.x, c.y, c.state), (500, 400, 'Idle'))
        keys.release('left')
        keys.release('down')
        game.update(c, keys, .1)
        x, y = c.x, c.y
        keys.release('right')
        game.update(c, keys, .1)
        self.assertEqual(c.x, x)
        self.assertEqual(c.y, y + 25)

    def test_corners_and_escape_from_boundary(self):
        for horizontal, x in [('left', 50), ('right', 950)]:
            for vertical, y in [('down', 50), ('up', 750)]:
                c, keys = game.Character(), game.Controls()
                keys.press(horizontal)
                keys.press(vertical)
                game.update(c, keys, 100)
                self.assertEqual((c.x, c.y), (x, y))
                keys.pressed.clear()
                keys.press('right' if horizontal == 'left' else 'left')
                game.update(c, keys, .1)
                self.assertTrue(50 < c.x < 950)
                self.assertEqual(c.y, y)

    def test_sliding_along_boundary(self):
        c, keys = game.Character(x=950), game.Controls()
        keys.press('right')
        keys.press('up')
        game.update(c, keys, .1)
        self.assertEqual(c.x, 950)
        self.assertGreater(c.y, 400)
        self.assertEqual(c.state, 'Run')

    def test_animation_wrap_rows_and_transitions(self):
        c = game.Character()
        game.animate(c, game.IDLE_INTERVAL * 10)
        self.assertEqual(c.frame, 2)
        for state, facing, bottom in [('Idle', 'right', 302),
                                     ('Idle', 'left', 202),
                                     ('Run', 'right', 102),
                                     ('Run', 'left', 2)]:
            c.state, c.facing = state, facing
            self.assertEqual(game.sprite_rectangle(c, 402), (200, bottom, 100, 100))
        c.state, c.facing = 'Idle', 'right'
        game.update_state(c, -1, 0)
        self.assertEqual((c.state, c.facing, c.frame, c.animation_time),
                         ('Run', 'left', 0, 0))
        game.animate(c, game.RUN_INTERVAL * 9)
        self.assertEqual(c.frame, 1)

    def test_update_frequency_independence(self):
        keys = game.Controls()
        keys.press('right')
        keys.press('up')
        slow, fast = game.Character(), game.Character()
        for _ in range(10):
            game.update(slow, keys, .1)
        for _ in range(100):
            game.update(fast, keys, .01)
        self.assertAlmostEqual(slow.x, fast.x)
        self.assertAlmostEqual(slow.y, fast.y)
        self.assertEqual(slow.frame, fast.frame)

    def test_events_repeat_focus_loss_and_exit(self):
        import pico2d as pico
        keys = game.Controls()
        def process(events):
            fake = SimpleNamespace(**{name: getattr(pico, name) for name in
                ('SDLK_LEFT', 'SDLK_RIGHT', 'SDLK_UP', 'SDLK_DOWN', 'SDLK_ESCAPE',
                 'SDL_QUIT', 'SDL_KEYDOWN', 'SDL_KEYUP', 'SDL_WINDOWEVENT',
                 'SDL_WINDOWEVENT_FOCUS_LOST')})
            fake.get_events = lambda: events
            return game.handle_events(fake, keys)
        right = SimpleNamespace(type=pico.SDL_KEYDOWN, key=pico.SDLK_RIGHT)
        self.assertTrue(process([right, right]))
        self.assertEqual(keys.pressed, {'right'})
        process([SimpleNamespace(type=pico.SDL_KEYUP, key=pico.SDLK_RIGHT)])
        self.assertFalse(keys.pressed)
        process([right, SimpleNamespace(type=pico.SDL_WINDOWEVENT,
                                       event=pico.SDL_WINDOWEVENT_FOCUS_LOST)])
        self.assertFalse(keys.pressed)
        self.assertFalse(process([SimpleNamespace(type=pico.SDL_QUIT)]))
        self.assertFalse(process([SimpleNamespace(type=pico.SDL_KEYDOWN,
                                                 key=pico.SDLK_ESCAPE)]))

    def test_missing_asset_error_includes_filename(self):
        with self.assertRaisesRegex(FileNotFoundError, 'missing-test.png'):
            game.asset_path('missing-test.png')


if __name__ == '__main__':
    unittest.main()
