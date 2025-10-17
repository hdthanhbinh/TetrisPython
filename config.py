"""
config.py
----------
Chứa các hằng số cấu hình của game Tetris:
- Kích thước board, margin, side panel
- Tốc độ, fonts, màu sắc
- USEREVENT
"""
import pygame as pg

# Kích thước cho board chính
BOARD_WIDTH, COLUMNS, ROWS = 340, 13, 26
DISTANCE = BOARD_WIDTH // COLUMNS
BOARD_HEIGHT = DISTANCE * ROWS

# Vùng bên phải cho Next/Score/Record
SIDE_PANEL_WIDTH = 300
MARGIN_LEFT = 40
MARGIN_TOP = 30

# Tổng kích thước cửa sổ
WINDOW_WIDTH = BOARD_WIDTH + SIDE_PANEL_WIDTH + MARGIN_LEFT*2
WINDOW_HEIGHT = BOARD_HEIGHT + MARGIN_TOP*2

# Tốc độ
START_SPEED = 800  # ms cho 1 bước rơi xuống
# Tốc độ giữ phím (ms)
MOVE_REPEAT_MS      = 90   # giữ ←/→ lặp mỗi 90ms
SOFT_DROP_REPEAT_MS = 30   # giữ ↓ rơi nhanh mỗi 30ms
ROTATE_REPEAT_MS    = 150  # (nếu muốn chặn xoay quá nhanh)

# mốc thời gian lần cuối di chuyển
last_move_left  = 0
last_move_right = 0
last_move_down  = 0
last_rotate     = 0

# Fonts
pg.font.init()
FONT_BIG = pg.font.SysFont("Arial", 36, bold=True)
FONT_SMALL = pg.font.SysFont("Arial", 24, bold=True)

# Màu
BLACK = (0,0,0)
WHITE = (255,255,255)
YELLOW = (255,255,0)
RED = (255,0,0)
BLUE_DARK = (0,0,64)

# USEREVENT
TETROROMINO_DOWN = pg.USEREVENT + 1
