import pygame as pg
import pygame_gui
import os, sys
from config import *
import math

def resource_path(*parts: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    return os.path.join(base, *parts)

class GameUI:
    """UI cho Tetris: panel CONTROL với 3 nút Pause/Restart/Quit"""

    def __init__(self, screen_size, theme_path=None,
                 on_toggle_pause=None, on_restart=None, on_quit=None):
        self.manager = pygame_gui.UIManager(screen_size, theme_path)
        self.flash_text: str | None = None
        self.flash_start = 0
        self.flash_ms = 0
        self.on_toggle_pause = on_toggle_pause
        self.on_restart = on_restart
        self.on_quit = on_quit

        icon_size = 50
        self.btn_pause = pygame_gui.elements.UIButton(
            pg.Rect(0, 0, icon_size, icon_size), text='', manager=self.manager, tool_tip_text="Pause/Resume")
        self.btn_restart = pygame_gui.elements.UIButton(
            pg.Rect(0, 0, icon_size, icon_size), text='', manager=self.manager, tool_tip_text="Restart")
        self.btn_quit = pygame_gui.elements.UIButton(
            pg.Rect(0, 0, icon_size, icon_size), text='', manager=self.manager, tool_tip_text="Quit")

        def _load_icon(path, size=40):
            surf = pg.image.load(path).convert_alpha()
            return pg.transform.smoothscale(surf, (size, size))

        try:
            ICON_DIR = resource_path("img")
            self.img_pause = _load_icon(os.path.join(ICON_DIR, "pause.png"))
            self.img_play = _load_icon(os.path.join(ICON_DIR, "play.png"))
            self.img_restart = _load_icon(os.path.join(ICON_DIR, "restart.png"))
            self.img_quit = _load_icon(os.path.join(ICON_DIR, "quit.png"))
        except Exception as e:
            print("⚠️ Không thể tải icon:", e)
            self.img_pause = self._text_icon("||")
            self.img_play = self._text_icon("▶")
            self.img_restart = self._text_icon("R")
            self.img_quit = self._text_icon("X")

        self.controls_rect = pg.Rect(0, 0, 220, 90)
        self.paused = False
        self.dim_surface = None

    def _text_icon(self, txt: str, size: int = 40):
        font = pg.font.SysFont(None, size)
        surf = font.render(txt, True, (230, 230, 230))
        return surf

    def place_controls(self, x, y, w=220, h=90, gap=15):
        self.controls_rect = pg.Rect(x, y, w, h)
        b = self.btn_pause.relative_rect
        total = b.width * 3 + gap * 2
        start_x = x + (w - total) // 2
        by = y + (h - b.height) // 2 + 10

        self.btn_pause.set_relative_position((start_x, by))
        self.btn_restart.set_relative_position((start_x + b.width + gap, by))
        self.btn_quit.set_relative_position((start_x + (b.width + gap) * 2, by))

    def flash_center(self, text: str, duration_ms: int = 1200):
        self.flash_text = text
        self.flash_start = pg.time.get_ticks()
        self.flash_ms = duration_ms

    def process_event(self, event):
        if event.type == pg.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_pause:
                self.paused = not self.paused
                if self.on_toggle_pause:
                    self.on_toggle_pause(self.paused)
            elif event.ui_element == self.btn_restart:
                self.paused = False
                if self.on_restart:
                    self.on_restart()
            elif event.ui_element == self.btn_quit:
                if self.on_quit:
                    self.on_quit()
        self.manager.process_events(event)

    def update(self, dt: float) -> None:
        self.manager.update(dt)

    def update_hud(self, score: int, level: int, lines: int):
        pass

    def draw(self, screen: "pg.Surface") -> None:
        pg.draw.rect(screen, BLUE_DARK, self.controls_rect)
        pg.draw.rect(screen, YELLOW, self.controls_rect, 3, border_radius=10)

        title = FONT_SMALL.render("CONTROL", True, YELLOW)
        screen.blit(title, title.get_rect(midtop=(self.controls_rect.centerx, self.controls_rect.top + 6)))

        self.manager.draw_ui(screen)

        if self.flash_text and not self.paused:
            elapsed = pg.time.get_ticks() - self.flash_start
            if elapsed < self.flash_ms:
                txt_font = pg.font.SysFont(None, 54)
                txt_surf = txt_font.render(self.flash_text, True, (255, 255, 255))

                pad_x, pad_y = 24, 12
                box_w = txt_surf.get_width() + pad_x * 2
                box_h = txt_surf.get_height() + pad_y * 2

                cx, cy = screen.get_width() // 2, screen.get_height() // 2
                box_rect = pg.Rect(0, 0, box_w, box_h)
                box_rect.center = (cx, cy - 80)

                box = pg.Surface((box_w, box_h), pg.SRCALPHA)
                box.fill((0, 0, 0, 150))
                screen.blit(box, box_rect.topleft)
                pg.draw.rect(screen, YELLOW, box_rect, 3, border_radius=12)

                dy = int(2 * math.sin(elapsed / 90))
                screen.blit(txt_surf, (box_rect.centerx - txt_surf.get_width() // 2,
                                    box_rect.centery - txt_surf.get_height() // 2 + dy))
            else:
                self.flash_text = None

        pause_icon = self.img_play if self.paused else self.img_pause
        for btn, icon in (
            (self.btn_pause, pause_icon),
            (self.btn_restart, self.img_restart),
            (self.btn_quit, self.img_quit),
        ):
            r = btn.relative_rect
            screen.blit(icon, icon.get_rect(center=r.center))

        if self.paused:
            if self.dim_surface is None or self.dim_surface.get_size() != screen.get_size():
                self.dim_surface = pg.Surface(screen.get_size(), pg.SRCALPHA)
                self.dim_surface.fill((0, 0, 0, 120))
            screen.blit(self.dim_surface, (0, 0))
            font = pg.font.SysFont(None, 64)
            txt = font.render("Paused", True, (240, 240, 240))
            screen.blit(txt, txt.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
