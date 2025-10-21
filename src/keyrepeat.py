import pygame as pg

class KeyRepeat:
    """
    Bộ điều khiển giữ phím có delay & interval:
    - Nhấn 1 cái: di chuyển đúng 1 ô
    - Giữ phím: sau initial_delay mới lặp, mỗi interval 1 ô
    - Nhả phím: dừng ngay
    """
    def __init__(self, initial_delay=180, interval=60, drop_interval=35):
        self.initial_delay = initial_delay
        self.interval = interval
        self.drop_interval = drop_interval
        self.state = {
            pg.K_LEFT:  {"pressed": False, "next_time": 0},
            pg.K_RIGHT: {"pressed": False, "next_time": 0},
            pg.K_DOWN:  {"pressed": False, "next_time": 0},
        }

    def on_keydown(self, key):
        if key not in self.state:
            return None
        now = pg.time.get_ticks()
        s = self.state[key]
        s["pressed"] = True
        s["next_time"] = now + (self.initial_delay if key in (pg.K_LEFT, pg.K_RIGHT) else self.drop_interval)
        return "move_now"

    def on_keyup(self, key):
        if key in self.state:
            self.state[key]["pressed"] = False

    def poll(self):
        now = pg.time.get_ticks()
        actions = []
        for key, s in self.state.items():
            if s["pressed"] and now >= s["next_time"]:
                if key == pg.K_LEFT:
                    actions.append("left")
                    s["next_time"] = now + self.interval
                elif key == pg.K_RIGHT:
                    actions.append("right")
                    s["next_time"] = now + self.interval
                elif key == pg.K_DOWN:
                    actions.append("down")
                    s["next_time"] = now + self.drop_interval
        return actions
