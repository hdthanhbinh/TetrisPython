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

# khởi tạo Pygame
pg.init()
screen = pg.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
pg.display.set_caption('Tetris Game')
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
    new_level = score // 200 + 1  # Tăng level mỗi 50 điểm (code cũ: comment ghi 100 điểm, mình sửa comment cho khớp công thức)
    if new_level > level:
        level = new_level
        # đặt giới hạn tối thiểu của tốc độ và tăng giảm tốc độ theo cấp
        # speed = max(100, START_SPEED - (level - 1) * 200)
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
next_tetro = rnd.choice(TETROROMINOS)
character = Tetroromino(next_tetro)
next_tetro = rnd.choice(TETROROMINOS)
grid = [0] * (COLUMNS * ROWS)
game_over = False
status = True
move_left = move_right = move_down = False
move_delay = 0  # Để kiểm soát tốc độ lặp lại khi giữ phím
paused = False
# 🟩 [NEW] bổ sung biến đệm để tránh NameError trong move_piece (code cũ: dùng nhưng chưa khai báo ban đầu)
left_pressed = right_pressed = down_pressed = False

# 🟩 [NEW] Hàm đồng bộ trạng thái Pause giữa logic & UI
def set_paused(state: bool):
    global paused
    paused = state
    try:
        ui.paused = state               # đồng bộ UI overlay
        ui.btn_pause.set_text('Resume' if state else 'Pause')  # đồng bộ nhãn nút
    except Exception:
        pass

# 🟩 [NEW] gom logic reset game để dùng cho nút Restart (code cũ: reset rải trong KEYUP khi game_over)
def reset_game():
    global grid, score, level, character, next_tetro, game_over, paused, speed
    grid = [0] * (COLUMNS * ROWS)
    score = 0
    level = 1
    speed = START_SPEED
    pg.time.set_timer(TETROROMINO_DOWN, speed)
    next_tetro = rnd.choice(TETROROMINOS)
    character = Tetroromino(next_tetro)
    next_tetro = rnd.choice(TETROROMINOS)
    game_over = False
    set_paused(False)  # 🟩 [NEW] đảm bảo UI & logic đều không còn pause

def move_piece():
    # 🟧 [CHANGED] Dùng tick (ms) để lặp khi giữ phím cho mượt & dễ chỉnh
    global last_move_left, last_move_right, last_move_down
    now = pg.time.get_ticks()

    if move_left and now - last_move_left >= MOVE_REPEAT_MS:
        character.update(grid, ROWS, COLUMNS, 0, -1)
        last_move_left = now

    if move_right and now - last_move_right >= MOVE_REPEAT_MS:
        character.update(grid, ROWS, COLUMNS, 0, 1)
        last_move_right = now

    if move_down and now - last_move_down >= SOFT_DROP_REPEAT_MS:
        # rơi nhanh khi giữ ↓
        character.update(grid, ROWS, COLUMNS, 1, 0)
        last_move_down = now


# 🟩 [NEW] callback cho UI (Pause/Restart/Quit)
def handle_toggle_pause(is_paused: bool):
    # code cũ: toggle bằng phím => giờ đồng bộ thêm từ UI
    set_paused(is_paused)

def handle_restart():
    # code cũ: reset trong KEYUP khi game_over => giờ gom vào reset_game()
    reset_game()

def handle_quit():
    # Thoát game khi bấm nút Quit trên UI
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

# ================= vòng lặp game =====================
while status:
    # 🟧 [CHANGED] dùng clock.tick để có dt cho UI thay vì pg.time.delay(100)
    # code cũ: pg.time.delay(100)
    dt = clock.tick(60) / 1000.0

    if not game_over and not paused:
        move_piece()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            status = False

        # 🟩 [NEW] chuyển sự kiện cho UI (nút Pause/Restart/Quit)
        ui.process_event(event)

        # 🟧 [CHANGED] gộp KEYDOWN vào 1 khối duy nhất
        if event.type == pg.KEYDOWN:
            # === Toggle Pause bằng SPACE ===
            if event.key == pg.K_SPACE:
                # 🟧 [CHANGED] dùng hàm đồng bộ
                set_paused(not paused)
                continue  # 🟩 sau khi toggle, bỏ qua xử lý phím khác của frame này

            # === Toggle Pause bằng ESC ===
            if event.key == pg.K_ESCAPE:
                # 🟧 [CHANGED] dùng hàm đồng bộ
                set_paused(not paused)
                continue

            # 🟩 [NEW] nếu đang pause -> không xử lý phím game
            if paused:
                continue

            # 🟩 nếu game over thì bỏ qua phím game (tuỳ bạn)
            if game_over:
                continue

            # === DI CHUYỂN / RƠI NHANH (bước đầu) ===
            if event.key == pg.K_LEFT:
                move_left = True;  left_pressed = True
                character.update(grid, ROWS, COLUMNS, 0, -1)
                last_move_left = pg.time.get_ticks()    # 🟩 [NEW] mốc lặp giữ phím

            elif event.key == pg.K_RIGHT:
                move_right = True; right_pressed = True
                character.update(grid, ROWS, COLUMNS, 0, 1)
                last_move_right = pg.time.get_ticks()   # 🟩 [NEW]

            elif event.key == pg.K_DOWN:
                move_down = True;  down_pressed = True
                character.update(grid, ROWS, COLUMNS, 1, 0)  # bước đầu rơi nhanh
                last_move_down = pg.time.get_ticks()    # 🟩 [NEW]

            elif event.key == pg.K_UP:
                # 🟩 [NEW] (tuỳ chọn) chặn xoay quá nhanh
                now = pg.time.get_ticks()
                if now - last_rotate >= ROTATE_REPEAT_MS:
                    character.rotate(grid, ROWS, COLUMNS)
                    last_rotate = now

        # 🟩 [NEW] Sự kiện timer rơi tự động (gravity)
        if event.type == TETROROMINO_DOWN and not paused and not game_over:
            if not character.update(grid, ROWS, COLUMNS, 1, 0):
                ObjectOnGridline(grid, character, COLUMNS)
                UpdateScore(4)
                DeleteAllRows(grid, ROWS, COLUMNS, UpdateScore)
                character = Tetroromino(next_tetro)
                next_tetro = rnd.choice(TETROROMINOS)
                if not character.check(grid, ROWS, COLUMNS, character.row, character.column):
                    game_over = True

        # 🟧 [CHANGED] KEYUP: tắt cờ giữ phím, reset khi game_over
        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                move_left = False;  left_pressed = False
            elif event.key == pg.K_RIGHT:
                move_right = False; right_pressed = False
            elif event.key == pg.K_DOWN:
                move_down = False;  down_pressed = False

            # 🟩 [NEW] nếu muốn nhấn phím bất kỳ để chơi lại khi game_over
            if game_over:
                reset_game()
                continue

    # vẽ background
    screen.blit(bg_image, (0,0))

    # board chính
    #board_rect = pg.Rect(MARGIN_LEFT, MARGIN_TOP, BOARD_WIDTH - 8 , BOARD_HEIGHT +3 )
    board_rect = pg.Rect(MARGIN_LEFT, MARGIN_TOP, BOARD_WIDTH , BOARD_HEIGHT  )
    for r in range(ROWS):
        for c in range(COLUMNS):
            x = MARGIN_LEFT + c * DISTANCE
            y = MARGIN_TOP + r * DISTANCE
            screen.blit(picture[0], (x, y))
    # pg.draw.rect(screen, YELLOW, board_rect, 2)     
    # pg.draw.rect(screen, YELLOW, board_rect, 2)       đáng lẽ là vẽ viền luôn nhưng mà grid đè -> xấu => vẽ sau grid

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

    # giờ mới vẽ viền nè
    pg.draw.rect(screen, YELLOW, board_rect, 2)

    # panel bên phải
    panel_x = MARGIN_LEFT + BOARD_WIDTH + 70

    ui.place_controls(panel_x, 40, 200, 130)  # 🟩 [NEW] đặt vị trí cụm nút UI
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
        # screen.blit(shadow, (WINDOW_WIDTH//2 - shadow.get_width()//2 + 3, WINDOW_HEIGHT//2 - shadow.get_height()//2 + 3 -40))
        screen.blit(text_gameover, (WINDOW_WIDTH//2 - text_gameover.get_width()//2,
                                WINDOW_HEIGHT//2 - text_gameover.get_height()//2 -40))

        # PRESS ANY KEY
        msg = "PRESS any key to play again"
        text_restart = FONT_SMALL.render(msg, True, WHITE)
        outline = FONT_SMALL_SHADOW.render(msg, True, SHADOW_VIOLET)
        # screen.blit(outline, (WINDOW_WIDTH//2 - outline.get_width()//2 + 2, WINDOW_HEIGHT//2 + text_gameover.get_height()//2 + 0 + 2))
        screen.blit(text_restart, (WINDOW_WIDTH//2 - text_restart.get_width()//2,
                               WINDOW_HEIGHT//2 + text_gameover.get_height()//2 + 0))


    # 🟩 [NEW] cập nhật & vẽ UI nằm trên cùng (bao gồm overlay khi pause)
    ui.update_hud(score, level, 0)  # code cũ: chưa có biến 'lines', tạm truyền 0
    ui.update(dt)
    ui.draw(screen)

    pg.display.flip()

pg.quit()
