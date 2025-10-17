"""
board.py
--------
Chứa các hàm quản lý grid:
- ObjectOnGridline: gắn tetromino vào grid
- DeleteAllRows: xóa các hàng đầy và cập nhật điểm
"""
from config import *

def ObjectOnGridline(grid, character, columns):
    for n, color in enumerate(character.tetro):
        if color > 0:
            grid[(character.row + n//4)*columns + (character.column + n%4)] = color

def DeleteAllRows(grid, rows, columns, UpdateScore):
    rows_cleared = 0
    for row in range(rows - 1, -1, -1):
        start = row * columns
        for column in range(columns):
            if grid[start + column] == 0:
                break
        else:
            del grid[start : start + columns]
            grid[0:0] = [0] * columns
            rows_cleared += 1
    if rows_cleared == 1:
        UpdateScore(50)
    elif rows_cleared > 1:
        sco = 50 * (2**(rows_cleared - 1) + 1)
        UpdateScore(sco)
