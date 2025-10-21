import random as rnd

class PieceBag:
    """
    7-bag randomizer: mỗi túi có đủ 7 tetromino, xáo trộn rồi rút hết mới nạp túi mới.
    Đảm bảo không "khát gậy" I quá lâu.
    """
    def __init__(self, pieces):
        # pieces: iterable các ma trận 4x4 (TETROROMINOS)
        self._pool = list(pieces)
        self._bag = []

    def _refill(self):
        self._bag = self._pool[:]
        rnd.shuffle(self._bag)

    def next(self):
        if not self._bag:
            self._refill()
        return self._bag.pop()
