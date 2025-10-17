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
START_SPEED = 500

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
