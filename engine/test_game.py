from engine import Engine

engine = Engine(white_playing = True, black_playing = True)

engine.print_board()

while True:
    print("White move: ", end="")
    move = input()
    engine.move_white(move)

    engine.print_board()

    print("Black move: ", end="")
    move = input()
    engine.move_black(move)

    engine.print_board()
    