"""
Main build-ready (fixed):
- Defines `grid` before first use (avoids NameError).
- Robust resource_path(): uses parent-of-src when running from source, and MEIPASS when bundled.
"""
import sys, os, random as rnd
import pygame as pg

from config import *
from tetromino import Tetroromino, TETROROMINOS
from board import ObjectOnGridline, DeleteAllRows
from utils import GetGhostRow
from ui_layer import GameUI
from keyrepeat import KeyRepeat
from gamestate import GameState
from piece_bag import PieceBag
from hud import draw_hud

# -------- resource resolver (works in .exe & in source tree) --------
def resource_path(*parts: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS  # PyInstaller extraction dir
    else:
        # Running from source: base is the project root (parent of src)
        base = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    return os.path.join(base, *parts)

IMG_DIR = resource_path("img")

# ---------------- Init ----------------
pg.init()
screen = pg.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
pg.display.set_caption('Tetris Game')
try:
    pg.key.set_repeat()  # disable OS repeat
except Exception:
    pass
clock = pg.time.Clock()

# Ảnh
picture = [pg.transform.scale(pg.image.load(os.path.join(IMG_DIR, f"b_{n}.jpg")), (DISTANCE, DISTANCE)) for n in range(8)]
bg_image = pg.image.load(os.path.join(IMG_DIR, "background.jpg"))
bg_image = pg.transform.scale(bg_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
appIcon = pg.image.load(os.path.join(IMG_DIR, "logo.png"))
pg.display.set_icon(appIcon)

# UI & State helpers
def set_paused(p: bool):
    global paused
    paused = p
    try:
        ui.paused = p
        ui.btn_pause.set_text('Resume' if p else 'Pause')
    except Exception:
        pass

def reset_game():
    global grid, next_tetro, character, game_over
    grid = [0] * (COLUMNS * ROWS)
    state.speed = START_SPEED
    state.score = 0
    state.level = 1
    pg.time.set_timer(TETROROMINO_DOWN, state.speed)
    next_tetro = bag.next()
    character = Tetroromino(next_tetro)
    next_tetro = bag.next()
    game_over = False
    set_paused(False)

def quit_game():
    pg.quit()
    sys.exit(0)

ui = GameUI(
    screen_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
    on_toggle_pause=lambda p: set_paused(p),
    on_restart=lambda: reset_game(),
    on_quit=lambda: quit_game(),
)

state = GameState(ui=ui)
paused = False
game_over = False
status = True

# Game init with 7-bag
bag = PieceBag(TETROROMINOS)
next_tetro = bag.next()
character = Tetroromino(next_tetro)
next_tetro = bag.next()

# ✅ Define grid BEFORE the loop (prevents NameError)
grid = [0] * (COLUMNS * ROWS)

# Input repeat
keyrep = KeyRepeat(initial_delay=180, interval=60, drop_interval=35)

# ---------------- Loop ----------------
while status:
    dt = clock.tick(60) / 1000.0

    for event in pg.event.get():
        if event.type == pg.QUIT:
            status = False

        ui.process_event(event)

        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_SPACE, pg.K_ESCAPE):
                set_paused(not paused)
                continue
            if paused or game_over:
                continue
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
            if game_over:
                reset_game()
                continue

        if event.type == TETROROMINO_DOWN and not paused and not game_over:
            if not character.update(grid, ROWS, COLUMNS, 1, 0):
                ObjectOnGridline(grid, character, COLUMNS)
                state.update_score(4)
                DeleteAllRows(grid, ROWS, COLUMNS, state.update_score)
                character = Tetroromino(next_tetro)
                next_tetro = bag.next()
                if not character.check(grid, ROWS, COLUMNS, character.row, character.column):
                    game_over = True

    if not paused and not game_over:
        for act in keyrep.poll():
            if act == "left":
                character.update(grid, ROWS, COLUMNS, 0, -1)
            elif act == "right":
                character.update(grid, ROWS, COLUMNS, 0, 1)
            elif act == "down":
                character.update(grid, ROWS, COLUMNS, 1, 0)

    # ---- Draw ----
    screen.blit(bg_image, (0, 0))

    board_rect = pg.Rect(MARGIN_LEFT, MARGIN_TOP, BOARD_WIDTH, BOARD_HEIGHT)
    for r in range(ROWS):
        for c in range(COLUMNS):
            x = MARGIN_LEFT + c * DISTANCE
            y = MARGIN_TOP + r * DISTANCE
            screen.blit(picture[0], (x, y))

    if not game_over:
        ghost_row = GetGhostRow(grid, character.tetro, character.row, character.column, ROWS)
        for n, color in enumerate(character.tetro):
            if color > 0:
                x = MARGIN_LEFT + (character.column + n % 4) * DISTANCE
                y = MARGIN_TOP + (ghost_row + n // 4) * DISTANCE
                ghost_img = picture[color].copy()
                ghost_img.set_alpha(100)
                screen.blit(ghost_img, (x, y))

    if not game_over:
        character.show(screen, picture, MARGIN_LEFT, MARGIN_TOP, DISTANCE)

    for n, color in enumerate(grid):
        if color > 0:
            x = MARGIN_LEFT + n % COLUMNS * DISTANCE
            y = MARGIN_TOP + n // COLUMNS * DISTANCE
            screen.blit(picture[color], (x, y))

    pg.draw.rect(screen, YELLOW, board_rect, 2)

    draw_hud(screen, ui, state, next_tetro, picture)

    ui.update_hud(state.score, state.level, 0)
    ui.update(dt)
    ui.draw(screen)

    pg.display.flip()

pg.quit()
