from stockfish import Stockfish
PATH = "/opt/homebrew/Cellar/stockfish/17/bin/stockfish"

__all__ = ["Engine"]


class Engine:

    def __init__(self, elo: int = 1000, white_playing: bool = False, black_playing: bool = False):
        self.stockfish = Stockfish(path=PATH)
        self.stockfish.set_elo_rating(elo)
        self.turn = False  # False represents white turn, True represents Black turn
        self.white = white_playing
        self.black = black_playing

    def print_board(self):
        print(self.stockfish.get_board_visual())

    def move_white(self, move: str = None):
        if not self.stockfish.is_move_correct(move):
            raise Exception("Illegal Move")
        if self.turn:
            raise Exception("It is not white's turn")
        if move is None:
            move = self.stockfish.get_best_move_time(500)
        self.stockfish.make_moves_from_current_position([move])
        if not self.black:
            self.stockfish.make_moves_from_current_position(
                [self.stockfish.get_best_move_time(500)])
        else:
            self.turn = not self.turn

    def move_black(self, move: str = None):
        if not self.stockfish.is_move_correct(move):
            raise Exception("Illegal Move")
        if not self.turn:
            raise Exception("It is not black's turn")
        if move is None:
            move = self.stockfish.get_best_move_time(500)
        self.stockfish.make_moves_from_current_position([move])
        if not self.white:
            self.stockfish.make_moves_from_current_position(
                [self.stockfish.get_best_move_time(500)])
        else:
            self.turn = not self.turn

    # for i in range(20):
    #     stockfish.make_moves_from_current_position([stockfish.get_best_move_time(500)])

    # print(stockfish.get_board_visual())
