"""
tetromino.py
------------
Chứa class Tetroromino và danh sách các hình dạng khối:
- Tetroromino: xoay, di chuyển, kiểm tra va chạm
- Danh sách các khối sẵn có (O, I, J, L, S, Z, T)
"""
import random as rnd
from dataclasses import dataclass
from config import *
import pygame as pg

# Danh sách các hình khối
TETROROMINOS = [
    [0,0,0,0, 0,1,1,0, 0,1,1,0, 0,0,0,0],  # O
    [0,0,0,0, 2,2,2,2, 0,0,0,0, 0,0,0,0],  # I
    [0,0,0,0, 3,0,0,0, 3,3,3,0, 0,0,0,0],  # J
    [0,0,0,0, 0,0,4,0, 4,4,4,0, 0,0,0,0],  # L
    [0,0,0,0, 0,5,5,0, 5,5,0,0, 0,0,0,0],  # S
    [0,0,0,0, 6,6,0,0, 0,6,6,0, 0,0,0,0],  # Z
    [0,0,0,0, 7,7,7,0, 0,7,0,0, 0,0,0,0]   # T
]

@dataclass
class Tetroromino:
    tetro: list
    row: int = 0
    column: int = 5

    def show(self, screen, picture, margin_left, margin_top, distance):
        # Vẽ block hiện tại lên màn hình
        for n, color in enumerate(self.tetro):
            if color > 0:
                x = margin_left + (self.column + n % 4) * distance
                y = margin_top + (self.row + n // 4) * distance
                screen.blit(picture[color], (x, y))

    def check(self, grid, rows, columns, r, c):
        # Kiểm tra vị trí hợp lệ trên grid
        for n, color in enumerate(self.tetro):
            if color > 0:
                rs = r + n//4
                cs = c + n%4
                if cs < 0 or rs >= rows or cs >= columns or grid[rs * columns + cs] > 0:
                    return False
        return True

    def update(self, grid, rows, columns, r, c):
        # Di chuyển tetromino nếu hợp lệ
        if self.check(grid, rows, columns, self.row + r, self.column + c):
            self.row += r
            self.column += c
            return True
        return False

    def rotate(self, grid, rows, columns):
        # Xoay tetromino nếu hợp lệ, nếu không thì giữ nguyên
        # Không xoay nếu là khối O
        if self.tetro == TETROROMINOS[0]:
            return
        savetetro = self.tetro.copy()
        for n, color in enumerate(savetetro):
            self.tetro[(2-(n%4))*4 + (n//4)] = color
        if not self.check(grid, rows, columns, self.row, self.column):
            self.tetro = savetetro.copy()
