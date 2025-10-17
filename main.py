"""
main.py
-------
Vòng lặp chính của game Tetris:
- Khởi tạo màn hình, grid, tetromino
- Quản lý sự kiện phím và timer
- Vẽ board, tetromino, ghost piece, panel NEXT/SCORE/RECORD
"""

import os
import pygame as pg
import random as rnd
from config import *
from tetromino import Tetroromino, TETROROMINOS
from board import ObjectOnGridline, DeleteAllRows
from utils import GetGhostRow

pg.init()
screen = pg.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
pg.display.set_caption('Tetris Game')

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
    score += sco
    if record < score:
        record = score
        save_record(record)
    
    new_level = score // 50 + 1 # Tăng level mỗi 100 điểm
    if new_level > level:
        level = new_level
        speed = max(100, START_SPEED - (level - 1) * 200)  # đặt giới hạn tối thiểu của tốc độ và tăng giảm tốc độ theo cấp
        pg.time.set_timer(TETROROMINO_DOWN, speed)
        

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

def move_piece():
    global move_delay, left_pressed, right_pressed, down_pressed
    move_speed = 0.5
    # Chỉ di chuyển khi giữ phím, và bỏ qua frame đầu tiên sau khi nhấn
    if move_left and not left_pressed:
        if move_delay == 0:
            character.update(grid, ROWS, COLUMNS, 0, -1)
    if move_right and not right_pressed:
        if move_delay == 0:
            character.update(grid, ROWS, COLUMNS, 0, 1)
    if move_down and not down_pressed:
        if move_delay == 0:
            character.update(grid, ROWS, COLUMNS, 1, 0)
    if move_left or move_right or move_down:
        move_delay = (move_delay + 1) % move_speed
    else:
        move_delay = 0
    # Sau frame đầu tiên, reset biến đệm
    left_pressed = right_pressed = down_pressed = False

# ================= vòng lặp game =====================
while status:
    pg.time.delay(100)
    if not game_over and not paused:
        move_piece()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            status = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:  # Nhấn Space để dừng/tiếp tục
                paused = not paused
                continue  # Không xử lý các phím khác khi vừa pause/unpause

        # Nếu đang pause, bỏ qua tất cả sự kiện khác (trừ SPACE)
        if paused:
            continue

        if not game_over:
            if event.type == TETROROMINO_DOWN:
                if not character.update(grid, ROWS, COLUMNS, 1, 0):
                    ObjectOnGridline(grid, character, COLUMNS)
                    UpdateScore(4)
                    DeleteAllRows(grid, ROWS, COLUMNS, UpdateScore)
                    character = Tetroromino(next_tetro)
                    next_tetro = rnd.choice(TETROROMINOS)
                    if not character.check(grid, ROWS, COLUMNS, character.row, character.column):
                        game_over = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                paused = not paused # Nhấn ESC để dừng/tiếp tục
            if event.key == pg.K_LEFT:
                move_left = True
                left_pressed = True
                character.update(grid, ROWS, COLUMNS, 0, -1)
            if event.key == pg.K_RIGHT:
                move_right = True
                right_pressed = True
                character.update(grid, ROWS, COLUMNS, 0, 1)
            if event.key == pg.K_DOWN:
                move_down = True
                down_pressed = True
                character.update(grid, ROWS, COLUMNS, 1, 0)
                character.update(grid, ROWS, COLUMNS, 1, 0)
            if event.key == pg.K_UP:
                character.rotate(grid, ROWS, COLUMNS)

        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                move_left = False
                left_pressed = False
            if event.key == pg.K_RIGHT:
                move_right = False
                right_pressed = False
            if event.key == pg.K_DOWN:
                move_down = False
                down_pressed = False
            if paused or game_over:
                if event.type == pg.KEYUP and game_over:
                    grid = [0] * (COLUMNS * ROWS)
                    score = 0
                    level = 1
                    character = Tetroromino(rnd.choice(TETROROMINOS))
                    game_over = False
                continue  # Không xử lý các phím khác khi đang pause/unpause

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
    panel_x = MARGIN_LEFT + BOARD_WIDTH + 60

    # NEXT
    next_rect = pg.Rect(panel_x, 80, 200, 160)
    pg.draw.rect(screen, BLUE_DARK, next_rect)
    pg.draw.rect(screen, YELLOW, next_rect, 3, border_radius=10)
    text_next = FONT_SMALL.render("NEXT", True, YELLOW)
    screen.blit(text_next, (next_rect.centerx - text_next.get_width()//2, next_rect.y + 5))

    demo_tetro = next_tetro  # demo NEXT
    for n, color in enumerate(demo_tetro):
        if color > 0:
            x = next_rect.centerx + (n % 4 - 2) * DISTANCE
            y = next_rect.centery + (n // 4 - 2) * DISTANCE
            screen.blit(picture[color], (x+2, y))

    # SCORE
    score_rect = pg.Rect(panel_x, 280, 200, 100)
    pg.draw.rect(screen, BLUE_DARK, score_rect)
    pg.draw.rect(screen, YELLOW, score_rect, 3, border_radius=10)
    text_score = FONT_SMALL.render("SCORE", True, YELLOW)
    text_score_val = FONT_SMALL.render(str(score), True, YELLOW)
    screen.blit(text_score, (score_rect.centerx - text_score.get_width()//2, score_rect.y + 5))
    screen.blit(text_score_val, (score_rect.centerx - text_score_val.get_width()//2, score_rect.y + 40))

    # RECORD
    record_rect = pg.Rect(panel_x, 420, 200, 100)
    pg.draw.rect(screen, BLUE_DARK, record_rect)
    pg.draw.rect(screen, YELLOW, record_rect, 3, border_radius=10)
    text_record = FONT_SMALL.render("RECORD", True, YELLOW)
    text_record_val = FONT_SMALL.render(str(record), True, YELLOW)
    screen.blit(text_record, (record_rect.centerx - text_record.get_width()//2, record_rect.y + 5))
    screen.blit(text_record_val, (record_rect.centerx - text_record_val.get_width()//2, record_rect.y + 40))

    # LEVEL
    level_rect = pg.Rect(panel_x, 560, 200, 100)
    pg.draw.rect(screen, BLUE_DARK, level_rect)
    pg.draw.rect(screen, YELLOW, level_rect, 3, border_radius=10)
    text_level = FONT_SMALL.render("LEVEL", True, YELLOW)
    text_level_val = FONT_SMALL.render(str(level), True, YELLOW)
    screen.blit(text_level, (level_rect.centerx - text_level.get_width()//2, level_rect.y + 5))
    screen.blit(text_level_val, (level_rect.centerx - text_level_val.get_width()//2, level_rect.y + 40))

    # Game Over
    if game_over:
        text_gameover = FONT_BIG.render("GAME OVER", True, RED)
        screen.blit(text_gameover, (WINDOW_WIDTH//2 - text_gameover.get_width()//2,
                                     WINDOW_HEIGHT//2 - text_gameover.get_height()//2))

    # Hiển thị Stop/Start khi paused
    if paused and not game_over:
        text_paused = FONT_BIG.render("STOP/START", True, RED)
        screen.blit(text_paused, (WINDOW_WIDTH//2 - text_paused.get_width()//2,
                                   WINDOW_HEIGHT//2 - text_paused.get_height()//2))
        
    pg.display.flip()

pg.quit()
