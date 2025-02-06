from engine import Engine

engine = Engine(white_playing = True, black_playing = True)

print(engine.stockfish.is_move_correct("v1osdihfaa2"))

# engine.move_white('h2h3')
# engine.move_black()
# engine.print_board()