"""
utils.py
--------
Chứa các hàm phụ trợ:
- GetGhostRow: tính vị trí "ghost piece" của tetromino rơi xuống
"""
def GetGhostRow(grid, tetro, start_row, start_col, rows):
    row = start_row
    while True:
        for n, color in enumerate(tetro):
            if color > 0:
                r = row + n // 4
                c = start_col + n % 4
                if r >= rows or grid[r * 13 + c] > 0:
                    return row - 1
        row += 1
