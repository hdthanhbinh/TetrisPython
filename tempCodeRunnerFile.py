if paused or game_over:
            if event.type == pg.KEYUP and game_over:
                grid = [0] * (COLUMNS * ROWS)
                score = 0
                level = 1
                character = Tetroromino(rnd.choice(TETROROMINOS))
                game_over = False
            continue