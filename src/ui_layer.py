import pygame as pg
import pygame_gui
import os
from config import *
import math

class GameUI:
    """🟩 UI cho game Tetris: gồm panel CONTROL với 3 nút Pause/Restart/Quit"""

    def __init__(self, screen_size, theme_path=None,
                 on_toggle_pause=None, on_restart=None, on_quit=None):
        # 🟩 [NEW] Quản lý UI
        self.manager = pygame_gui.UIManager(screen_size, theme_path)
        # 🟩 [NEW] cấu hình & state cho thông báo giữa màn hình
        self.flash_text: str | None = None
        self.flash_start = 0
        self.flash_ms = 0
        # 🟩 [NEW] Callback sang main.py
        self.on_toggle_pause = on_toggle_pause
        self.on_restart = on_restart
        self.on_quit = on_quit

        # 🟧 [CHANGED] Nút vuông 50×50 (chỉ icon)
        icon_size = 50
        self.btn_pause = pygame_gui.elements.UIButton(
            pg.Rect(0, 0, icon_size, icon_size), text='', manager=self.manager, tool_tip_text="Pause/Resume")
        self.btn_restart = pygame_gui.elements.UIButton(
            pg.Rect(0, 0, icon_size, icon_size), text='', manager=self.manager, tool_tip_text="Restart")
        self.btn_quit = pygame_gui.elements.UIButton(
            pg.Rect(0, 0, icon_size, icon_size), text='', manager=self.manager, tool_tip_text="Quit")

        # 🟩 [NEW] Tải ảnh icon (đặt cùng thư mục)
        def _load_icon(name, size=40):
            surf = pg.image.load(name).convert_alpha()
            return pg.transform.smoothscale(surf, (size, size))

        ICON_DIR = os.path.join(os.path.dirname(__file__), "../img")

        try:
            self.img_pause = _load_icon(os.path.join(ICON_DIR, "pause.png"))
            self.img_play = _load_icon(os.path.join(ICON_DIR, "play.png"))          # Khi đang paused
            self.img_restart = _load_icon(os.path.join(ICON_DIR, "restart.png"))
            self.img_quit = _load_icon(os.path.join(ICON_DIR, "quit.png"))
        except Exception as e:
            print("⚠️ Không thể tải icon:", e)
            # fallback: vẽ chữ nếu thiếu icon
            self.img_pause = self._text_icon("||")
            self.img_play = self._text_icon("▶")
            self.img_restart = self._text_icon("R")
            self.img_quit = self._text_icon("X")

        # 🟩 [NEW] Panel CONTROL và trạng thái
        self.controls_rect = pg.Rect(0, 0, 220, 90)
        self.paused = False
        self.dim_surface = None

    # 🟩 [NEW] fallback: tạo ảnh từ text (dùng nếu không tải được icon)
    def _text_icon(self, txt: str, size: int = 40):
        font = pg.font.SysFont(None, size)
        surf = font.render(txt, True, (230, 230, 230))
        return surf

    # 🟧 [CHANGED] Bố trí nút icon nằm ngang, giữa panel CONTROL
    def place_controls(self, x, y, w=220, h=90, gap=15):
        """
        🟩 Đặt panel CONTROL và 3 nút icon nằm ngang, giữa panel
        """
        self.controls_rect = pg.Rect(x, y, w, h)
        b = self.btn_pause.relative_rect
        total = b.width * 3 + gap * 2
        start_x = x + (w - total) // 2
        by = y + (h - b.height) // 2 + 10

        self.btn_pause.set_relative_position((start_x, by))
        self.btn_restart.set_relative_position((start_x + b.width + gap, by))
        self.btn_quit.set_relative_position((start_x + (b.width + gap) * 2, by))
    def flash_center(self, text: str, duration_ms: int = 1200):
        """🟩 [NEW] Hiện một thông báo nhỏ giữa màn hình trong duration_ms."""
        self.flash_text = text
        self.flash_start = pg.time.get_ticks()
        self.flash_ms = duration_ms

    # 🟩 [NEW] Xử lý sự kiện từ các nút UI
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

        # 🟩 Chuyển tiếp sự kiện cho pygame_gui
        self.manager.process_events(event)

    # 🟩 [NEW] Cập nhật pygame_gui mỗi frame
    def update(self, dt: float) -> None:
        self.manager.update(dt)
    def update_hud(self, score: int, level: int, lines: int):
        # 🟩 [NEW] Nơi bạn có thể bổ sung label HUD của pygame_gui nếu muốn
        pass

    # 🟧 [CHANGED] Vẽ UI + khung + icon
    def draw(self, screen: "pg.Surface") -> None:
        # 🟩 Panel CONTROL (viền vàng, nền xanh đậm)
        pg.draw.rect(screen, BLUE_DARK, self.controls_rect)
        pg.draw.rect(screen, YELLOW, self.controls_rect, 3, border_radius=10)

        # 🟩 Tiêu đề CONTROL
        title = FONT_SMALL.render("CONTROL", True, YELLOW)
        screen.blit(title, title.get_rect(midtop=(self.controls_rect.centerx, self.controls_rect.top + 6)))

        # 🟩 Vẽ nền & hover nút từ pygame_gui
        self.manager.draw_ui(screen)
        # 🟩 [NEW] Thông báo nhỏ giữa màn hình (LEVEL UP!, v.v.)
        if self.flash_text and not self.paused:
            elapsed = pg.time.get_ticks() - self.flash_start
            if elapsed < self.flash_ms:
                # khung mờ nhỏ giữa màn hình
                txt_font = pg.font.SysFont(None, 54)
                txt_surf = txt_font.render(self.flash_text, True, (255, 255, 255))

                pad_x, pad_y = 24, 12
                box_w = txt_surf.get_width() + pad_x * 2
                box_h = txt_surf.get_height() + pad_y * 2

                cx, cy = screen.get_width() // 2, screen.get_height() // 2
                box_rect = pg.Rect(0, 0, box_w, box_h)
                box_rect.center = (cx, cy - 80)  # hơi cao hơn giữa một chút

                # nền bán trong + viền vàng
                box = pg.Surface((box_w, box_h), pg.SRCALPHA)
                box.fill((0, 0, 0, 150))
                screen.blit(box, box_rect.topleft)
                pg.draw.rect(screen, YELLOW, box_rect, 3, border_radius=12)

                # hiệu ứng nhịp nhẹ
                t = elapsed / self.flash_ms
                dy = int(2 * math.sin(elapsed / 90))
                screen.blit(txt_surf, (box_rect.centerx - txt_surf.get_width() // 2,
                                    box_rect.centery - txt_surf.get_height() // 2 + dy))
            else:
                # hết thời gian -> tắt thông báo
                self.flash_text = None

        # 🟩 Vẽ icon vào giữa nút
        pause_icon = self.img_play if self.paused else self.img_pause
        for btn, icon in (
            (self.btn_pause, pause_icon),
            (self.btn_restart, self.img_restart),
            (self.btn_quit, self.img_quit),
        ):
            r = btn.relative_rect
            screen.blit(icon, icon.get_rect(center=r.center))

        # 🟩 Overlay "Paused"
        if self.paused:
            if self.dim_surface is None or self.dim_surface.get_size() != screen.get_size():
                self.dim_surface = pg.Surface(screen.get_size(), pg.SRCALPHA)
                self.dim_surface.fill((0, 0, 0, 120))
            screen.blit(self.dim_surface, (0, 0))
            font = pg.font.SysFont(None, 64)
            txt = font.render("Paused", True, (240, 240, 240))
            screen.blit(txt, txt.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
