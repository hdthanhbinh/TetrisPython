import os
import pygame as pg
from config import START_SPEED, TETROROMINO_DOWN

RECORD_FILE = "record.txt"

def load_record():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_record(value):
    with open(RECORD_FILE, "w") as f:
        f.write(str(value))

class GameState:
    def __init__(self, ui=None):
        self.ui = ui
        self.speed = START_SPEED
        self.score = 0
        self.record = load_record()
        self.level = 1
        pg.time.set_timer(TETROROMINO_DOWN, self.speed)

    def update_score(self, sco):
        old_level = self.level
        self.score += sco
        if self.record < self.score:
            self.record = self.score
            save_record(self.record)
        new_level = self.score // 200 + 1
        if new_level > self.level:
            self.level = new_level
            # tăng tốc rơi khi level tăng
            self.speed = int(self.speed * 0.8)
            self.speed = max(100, self.speed)
            pg.time.set_timer(TETROROMINO_DOWN, self.speed)
        if self.level > old_level and self.ui:
            self.ui.flash_center("LEVEL UP!", 1200)
