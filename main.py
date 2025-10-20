"""
Vòng lặp chính của game Tetris:
- Khởi tạo màn hình, grid, tetromino
- Quản lý sự kiện phím và timer
- Vẽ board, tetromino, ghost piece, panel NEXT/SCORE/RECORD
"""

import os
# 🟩 [NEW] cần sys để thoát ứng dụng khi bấm nút Quit trong UI
import sys  # code cũ: chưa import sys
import pygame as pg
import random as rnd
from config import *
from tetromino import Tetroromino, TETROROMINOS
from board import ObjectOnGridline, DeleteAllRows
from utils import GetGhostRow
from ui_layer import GameUI  # code cũ: đã import sẵn, nhưng chưa dùng
import math  

# -------------------------
# 🔧 Anti key-repeat (custom)
# -------------------------
class KeyRepeat:
    """
    Bộ điều khiển giữ phím có delay & interval rõ ràng:
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
import random as rnd

class PieceBag:
    def __init__(self, pieces):
        self.pieces = pieces[:]  # TETROROMINOS
        self.bag = []
    def next(self):
        if not self.bag:
            self.bag = self.pieces[:]
            rnd.shuffle(self.bag)
        return self.bag.pop()

# Khởi tạo
bag = PieceBag(TETROROMINOS)

# khởi tạo Pygame
pg.init()
screen = pg.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
pg.display.set_caption('Tetris Game')
# 🟧 [CHANGED] Disable OS repeat to tránh nhảy 2–3 ô khi nhấn nhanh
try:
    pg.key.set_repeat()  # gọi không tham số để tắt repeat mặc định
except Exception:
    pass

# 🟧 [CHANGED] dùng clock.tick để có dt cho pygame-gui (code cũ: vẫn có clock, nhưng phía dưới dùng pg.time.delay)
clock = pg.time.Clock()

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

def UpdateScore(sco):
    global score, record, level, speed
    old_level = level # lưu level cũ để so sánh
    score += sco
    if record < score:
        record = score
        save_record(record)
    new_level = score // 200 + 1  # Tăng level theo điểm
    if new_level > level:
        level = new_level
        # tăng tốc rơi khi level tăng
        speed = int(speed * 0.8)
        speed = max(100, speed)
        pg.time.set_timer(TETROROMINO_DOWN, speed)
    if level > old_level:
        ui.flash_center("LEVEL UP!", 1200)
        
# ảnh block
picture = []
for n in range(8):
    picture.append(pg.transform.scale(pg.image.load(f'b_{n}.jpg'), (DISTANCE, DISTANCE)))

# ảnh background
bg_image = pg.image.load("background.jpg")
bg_image = pg.transform.scale(bg_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

# logo
appIcon = pg.image.load("logo.png") 
pg.display.set_icon(appIcon)

# sự kiện
speed = START_SPEED
score = 0
record = load_record()
level = 1
pg.time.set_timer(TETROROMINO_DOWN, speed)

# khởi tạo game
next_tetro = bag.next()
character = Tetroromino(next_tetro)
next_tetro = bag.next()
grid = [0] * (COLUMNS * ROWS)
game_over = False
status = True
paused = False

# 🟩 [NEW] Hàm đồng bộ trạng thái Pause giữa logic & UI
def set_paused(state: bool):
    global paused
    paused = state
    try:
        ui.paused = state               # đồng bộ UI overlay
        ui.btn_pause.set_text('Resume' if state else 'Pause')  # đồng bộ nhãn nút (UI icon-only vẫn hoạt động)
    except Exception:
        pass

# 🟩 [NEW] gom logic reset game để dùng cho nút Restart
def reset_game():
    global grid, score, level, character, next_tetro, game_over, paused, speed
    grid = [0] * (COLUMNS * ROWS)
    score = 0
    level = 1
    speed = START_SPEED
    pg.time.set_timer(TETROROMINO_DOWN, speed)
    next_tetro = bag.next()
    character = Tetroromino(next_tetro)
    next_tetro = bag.next()
    game_over = False
    set_paused(False)  # đảm bảo UI & logic đều không còn pause

# 🟩 [NEW] callback cho UI (Pause/Restart/Quit)
def handle_toggle_pause(is_paused: bool):
    set_paused(is_paused)

def handle_restart():
    reset_game()

def handle_quit():
    pg.quit()
    sys.exit(0)

# 🟩 [NEW] tạo lớp UI (GameUI) để có nút Pause/Resume/Restart + overlay
ui = GameUI(
    screen_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
    theme_path=None,  # có thể thay bằng 'themes/dark.json'
    on_toggle_pause=handle_toggle_pause,
    on_restart=handle_restart,
    on_quit=handle_quit
)

# 🟩 [NEW] Khởi tạo bộ điều khiển auto-repeat
keyrep = KeyRepeat(initial_delay=180, interval=60, drop_interval=35)

# ================= vòng lặp game =====================
while status:
    # 🟧 [CHANGED] dùng clock.tick để có dt cho UI thay vì pg.time.delay(100)
    dt = clock.tick(60) / 1000.0

    for event in pg.event.get():
        if event.type == pg.QUIT:
            status = False

        # 🟩 chuyển sự kiện cho UI (nút Pause/Restart/Quit)
        ui.process_event(event)

        if event.type == pg.KEYDOWN:
            # Toggle Pause bằng SPACE/ESC
            if event.key in (pg.K_SPACE, pg.K_ESCAPE):
                set_paused(not paused)
                continue

            # Nếu đang pause hoặc game over, bỏ qua phím gameplay
            if paused or game_over:
                continue

            # --- Nhấn lần đầu: di chuyển đúng 1 bước ---
            if event.key in (pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN):
                if keyrep.on_keydown(event.key) == "move_now":
                    if event.key == pg.K_LEFT:
                        character.update(grid, ROWS, COLUMNS, 0, -1)
                    elif event.key == pg.K_RIGHT:
                        character.update(grid, ROWS, COLUMNS, 0, 1)
                    elif event.key == pg.K_DOWN:
                        character.update(grid, ROWS, COLUMNS, 1, 0)

            elif event.key == pg.K_UP:
                character.rotate(grid, ROWS, COLUMNS)

        elif event.type == pg.KEYUP:
            keyrep.on_keyup(event.key)

            # Nhấn phím bất kỳ để chơi lại khi game_over
            if game_over:
                reset_game()
                continue

        # Rơi tự động (gravity)
        if event.type == TETROROMINO_DOWN and not paused and not game_over:
            if not character.update(grid, ROWS, COLUMNS, 1, 0):
                ObjectOnGridline(grid, character, COLUMNS)
                UpdateScore(4)
                DeleteAllRows(grid, ROWS, COLUMNS, UpdateScore)
                character = Tetroromino(next_tetro)
                next_tetro = bag.next()
                if not character.check(grid, ROWS, COLUMNS, character.row, character.column):
                    game_over = True

    # Auto-repeat khi GIỮ phím (chỉ chạy khi đang chơi)
    if not paused and not game_over:
        for act in keyrep.poll():
            if act == "left":
                character.update(grid, ROWS, COLUMNS, 0, -1)
            elif act == "right":
                character.update(grid, ROWS, COLUMNS, 0, 1)
            elif act == "down":
                character.update(grid, ROWS, COLUMNS, 1, 0)

    # vẽ background
    screen.blit(bg_image, (0,0))

    # board chính
    board_rect = pg.Rect(MARGIN_LEFT, MARGIN_TOP, BOARD_WIDTH , BOARD_HEIGHT)
    for r in range(ROWS):
        for c in range(COLUMNS):
            x = MARGIN_LEFT + c * DISTANCE
            y = MARGIN_TOP + r * DISTANCE
            screen.blit(picture[0], (x, y))

    # ghost piece
    if not game_over:
        ghost_row = GetGhostRow(grid, character.tetro, character.row, character.column, ROWS)
        for n, color in enumerate(character.tetro):
            if color > 0:
                x = MARGIN_LEFT + (character.column + n % 4) * DISTANCE
                y = MARGIN_TOP + (ghost_row + n // 4) * DISTANCE
                ghost_img = picture[color].copy()
                ghost_img.set_alpha(100)
                screen.blit(ghost_img, (x, y))

    # block rơi
    if not game_over:
        character.show(screen, picture, MARGIN_LEFT, MARGIN_TOP, DISTANCE)

    # vẽ grid
    for n, color in enumerate(grid):
        if color > 0:
            x = MARGIN_LEFT + n % COLUMNS * DISTANCE
            y = MARGIN_TOP + n // COLUMNS * DISTANCE
            screen.blit(picture[color], (x, y))

    # viền board
    pg.draw.rect(screen, YELLOW, board_rect, 2)

    # panel bên phải
    panel_x = MARGIN_LEFT + BOARD_WIDTH + 70

    ui.place_controls(panel_x, 40, 200, 130)  # đặt vị trí cụm nút UI
    next_y = ui.controls_rect.bottom + 20
    
    # NEXT
    next_rect = pg.Rect(panel_x, next_y, 200, 150)
    pg.draw.rect(screen, BLUE_DARK, next_rect)
    pg.draw.rect(screen, YELLOW, next_rect, 3, border_radius=10)
    text_next = FONT_SMALL.render("NEXT", True, YELLOW)
    screen.blit(text_next, (next_rect.centerx - text_next.get_width()//2, next_rect.y + 5))

    # --- Căn giữa tetromino ---
    demo_tetro = next_tetro
    coords = [(n % 4, n // 4) for n, color in enumerate(demo_tetro) if color > 0]
    if coords:
        min_x = min(x for x, _ in coords)
        max_x = max(x for x, _ in coords)
        min_y = min(y for _, y in coords)
        max_y = max(y for _, y in coords)

        width = (max_x - min_x + 1) * DISTANCE
        height = (max_y - min_y + 1) * DISTANCE

        offset_x = next_rect.centerx - width // 2
        offset_y = next_rect.centery - height // 2 + 10  # 10px cho dễ nhìn

        for n, color in enumerate(demo_tetro):
            if color > 0:
                grid_x = n % 4
                grid_y = n // 4
                x = offset_x + (grid_x - min_x) * DISTANCE
                y = offset_y + (grid_y - min_y) * DISTANCE
                screen.blit(picture[color], (x, y))

    # SCORE
    score_rect  = pg.Rect(panel_x, next_rect.bottom  + 20, 200, 100)
    pg.draw.rect(screen, BLUE_DARK, score_rect)
    pg.draw.rect(screen, YELLOW, score_rect, 3, border_radius=10)
    text_score = FONT_SMALL.render("SCORE", True, YELLOW)
    text_score_val = FONT_SMALL.render(str(score), True, YELLOW)
    screen.blit(text_score, (score_rect.centerx - text_score.get_width()//2, score_rect.y + 5))
    screen.blit(text_score_val, (score_rect.centerx - text_score_val.get_width()//2, score_rect.y + 40))

    # RECORD
    record_rect = pg.Rect(panel_x, score_rect.bottom + 20, 200, 100)
    pg.draw.rect(screen, BLUE_DARK, record_rect)
    pg.draw.rect(screen, YELLOW, record_rect, 3, border_radius=10)
    text_record = FONT_SMALL.render("RECORD", True, YELLOW)
    text_record_val = FONT_SMALL.render(str(record), True, YELLOW)
    screen.blit(text_record, (record_rect.centerx - text_record.get_width()//2, record_rect.y + 5))
    screen.blit(text_record_val, (record_rect.centerx - text_record_val.get_width()//2, record_rect.y + 40))

    # LEVEL
    level_rect  = pg.Rect(panel_x, record_rect.bottom + 20, 200, 100)
    pg.draw.rect(screen, BLUE_DARK, level_rect)
    pg.draw.rect(screen, YELLOW, level_rect, 3, border_radius=10)
    text_level = FONT_SMALL.render("LEVEL", True, YELLOW)
    text_level_val = FONT_SMALL.render(str(level), True, YELLOW)
    screen.blit(text_level, (level_rect.centerx - text_level.get_width()//2, level_rect.y + 5))
    screen.blit(text_level_val, (level_rect.centerx - text_level_val.get_width()//2, level_rect.y + 40))

    if game_over:
        # GAME OVER
        dim_surface = pg.Surface(screen.get_size(), pg.SRCALPHA)
        dim_surface.fill((0, 0, 0, 120)) 
        screen.blit(dim_surface, (0, 0))

        text_gameover = FONT_BIG.render("GAME OVER", True, RED)
        shadow = FONT_BIG_SHADOW.render("GAME OVER", True, SHADOW_VIOLET)
        screen.blit(text_gameover, (WINDOW_WIDTH//2 - text_gameover.get_width()//2,
                                WINDOW_HEIGHT//2 - text_gameover.get_height()//2 -40))

        # PRESS ANY KEY
        msg = "PRESS any key to play again"
        text_restart = FONT_SMALL.render(msg, True, WHITE)
        outline = FONT_SMALL_SHADOW.render(msg, True, SHADOW_VIOLET)
        screen.blit(text_restart, (WINDOW_WIDTH//2 - text_restart.get_width()//2,
                               WINDOW_HEIGHT//2 + text_gameover.get_height()//2 + 0))

    # cập nhật & vẽ UI nằm trên cùng (bao gồm overlay khi pause)
    ui.update_hud(score, level, 0)  # tạm truyền 0 cho 'lines'
    ui.update(dt)
    ui.draw(screen)

    pg.display.flip()

pg.quit()
