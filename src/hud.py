import pygame as pg
from config import (
    MARGIN_LEFT, BOARD_WIDTH, BLUE_DARK, YELLOW, WHITE, DISTANCE,
    FONT_SMALL
)

def _draw_next_panel(screen, panel_x, next_tetro, picture):
    next_rect = pg.Rect(panel_x, panel_y:=40+130+20, 200, 150)  # 130 cao control, 20 gap
    pg.draw.rect(screen, BLUE_DARK, next_rect)
    pg.draw.rect(screen, YELLOW, next_rect, 3, border_radius=10)
    text_next = FONT_SMALL.render("NEXT", True, YELLOW)
    screen.blit(text_next, (next_rect.centerx - text_next.get_width()//2, next_rect.y + 5))

    # Căn giữa tetromino tiếp theo
    coords = [(n % 4, n // 4) for n, color in enumerate(next_tetro) if color > 0]
    if coords:
        min_x = min(x for x, _ in coords); max_x = max(x for x, _ in coords)
        min_y = min(y for _, y in coords); max_y = max(y for _, y in coords)
        width = (max_x - min_x + 1) * DISTANCE
        height = (max_y - min_y + 1) * DISTANCE
        offset_x = next_rect.centerx - width // 2
        offset_y = next_rect.centery - height // 2 + 10
        for n, color in enumerate(next_tetro):
            if color > 0:
                gx, gy = n % 4, n // 4
                x = offset_x + (gx - min_x) * DISTANCE
                y = offset_y + (gy - min_y) * DISTANCE
                screen.blit(picture[color], (x, y))
    return next_rect.bottom

def _panel(screen, x, y, title, value):
    rect = pg.Rect(x, y, 200, 100)
    pg.draw.rect(screen, BLUE_DARK, rect)
    pg.draw.rect(screen, YELLOW, rect, 3, border_radius=10)
    t = FONT_SMALL.render(title, True, YELLOW)
    v = FONT_SMALL.render(str(value), True, YELLOW)
    screen.blit(t, (rect.centerx - t.get_width()//2, rect.y + 5))
    screen.blit(v, (rect.centerx - v.get_width()//2, rect.y + 40))
    return rect.bottom

def draw_hud(screen, ui, state, next_tetro, picture):
    """Vẽ cụm nút CONTROL + panel NEXT/SCORE/RECORD/LEVEL ở bên phải."""
    panel_x = MARGIN_LEFT + BOARD_WIDTH + 70

    # Cụm nút CONTROL
    ui.place_controls(panel_x, 40, 200, 130)

    # NEXT
    bottom = _draw_next_panel(screen, panel_x, next_tetro, picture)

    # SCORE
    bottom = _panel(screen, panel_x, bottom + 20, "SCORE", state.score)

    # RECORD
    bottom = _panel(screen, panel_x, bottom + 20, "RECORD", state.record)

    # LEVEL
    _panel(screen, panel_x, bottom + 20, "LEVEL", state.level)
