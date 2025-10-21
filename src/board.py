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
    # Tạo danh sách mới gồm những hàng chưa đầy
    new_grid = []
    rows_cleared = 0

    for r in range(rows):
        start = r * columns
        row_data = grid[start:start + columns]
        if all(row_data):  # nếu hàng đầy (toàn giá trị khác 0)
            rows_cleared += 1
        else:
            new_grid.extend(row_data)

    # Thêm hàng trống ở đầu để giữ kích thước grid
    grid[:] = [0] * (rows_cleared * columns) + new_grid

    # Cập nhật điểm
    if rows_cleared == 1:
        UpdateScore(50)
    elif rows_cleared == 2:
        UpdateScore(150)
    elif rows_cleared == 3:
        UpdateScore(250)
    elif rows_cleared == 4:
        UpdateScore(400)
