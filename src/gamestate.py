import os
import sys
import shutil
import pygame as pg
from config import START_SPEED, TETROROMINO_DOWN

APP_NAME = "Pygame_Tetris"

def get_save_dir() -> str:
    """Trả về thư mục lưu dữ liệu (record.txt) theo hệ điều hành."""
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
        return os.path.join(base, APP_NAME)
    elif sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~/Library/Application Support"), APP_NAME)
    else:
        return os.path.join(os.path.expanduser("~/.local/share"), APP_NAME)

SAVE_DIR = get_save_dir()
os.makedirs(SAVE_DIR, exist_ok=True)

RECORD_FILE = os.path.join(SAVE_DIR, "record.txt")

# Di trú dữ liệu cũ nếu có
LEGACY_RECORD = os.path.join(os.getcwd(), "record.txt")
if os.path.exists(LEGACY_RECORD) and not os.path.exists(RECORD_FILE):
    try:
        shutil.copy2(LEGACY_RECORD, RECORD_FILE)
    except Exception:
        pass

def load_record():
    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip() or "0")
    except Exception:
        return 0

def save_record(value: int):
    try:
        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            f.write(str(int(value)))
    except Exception:
        pass

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
            self.speed = int(self.speed * 0.8)
            self.speed = max(100, self.speed)
            pg.time.set_timer(TETROROMINO_DOWN, self.speed)
        if self.level > old_level and self.ui:
            self.ui.flash_center("LEVEL UP!", 1200)
