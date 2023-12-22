from basics import *
from evaluation_values import *


class EvaluationRepository:
    def __init__(self):
        self._store = bytearray(MAX_INDEX + 1)  # will be initialized to 0 = UNKNOWN
        self.read_count = 0
        self.write_count = 0

    def store(self, position, evaluation):
        self._store[position.idx] = evaluation
        self.write_count += 1

    def __getitem__(self, position):
        self.read_count += 1
        return self._store[position.idx]

    def get_eval_board(self, pawns):
        # note pawns.idx-1 will be the value when the queen is on square 0 = INVALID_SQUARE
        return self._store[pawns.idx-1:pawns.idx + 64]

    def store_eval_board(self, pawns, eval_board):
        # note eval_board[0] will be the value when the queen is on square 0 = INVALID_SQUARE
        # so need not be stored
        self._store[pawns.idx:pawns.idx + 64] = eval_board[1:]

    def save_to_file(self, filename):
        with open(filename, "wb") as f:
            f.write(self._store)

    def load_from_file(self, filename):
        with open(filename, "rb") as f:
            self._store = bytearray(f.read())
        assert len(self._store) == MAX_INDEX + 1, len(self._store)

    @property
    def size(self):
        return len(self._store)

    def count(self, value):
        return self._store.count(value)

    def print_stats(self):
        print(f"Number of positions in store: {len(self._store)}")
        print(f"  Number of unknown position: {self._store.count(UNKNOWN)}")
        print(f"  Number of positions with draw: {self._store.count(DRAW)}")
        print(f"  Number of positions queen has won: {self._store.count(QUEEN_HAS_WON)}")
        print(f"  Number of positions with pawns win in 1 move: {self._store.count(PAWNS_WIN_IN_1)}")
        print(f"  Number of positions with queen win in 1 move: {self._store.count(QUEEN_WINS_IN_1)}")
        value_pawn_wins = PAWNS_WIN_IN_1
        value_queen_wins = QUEEN_WINS_IN_1
        for i in range(2, 40):
            value_pawn_wins = add_one_move(value_pawn_wins)
            count = self._store.count(value_pawn_wins)
            if count > 0:
                print(f"  Number of positions with pawns win in {i} moves: {count}")
            value_queen_wins = add_one_move(value_queen_wins)
            count = self._store.count(value_queen_wins)
            if count > 0:
                print(f"  Number of positions with queen win in {i} moves: {count}")

    def print_counts(self):
        print(f"Reads: {self.read_count}\tWrites: {self.write_count}")

    @staticmethod
    def code_to_position(code):
        queen = code % 64 + 1
        code //= 64
        pawns = []
        for f in FILES:
            r = code % 6
            code //= 6
            if r != 0:
                pawns.append(FILE_RANK_TO_SQUARE[f][r + 1])
        return Position(Pawns(pawns), queen)


def print_repo_stats():
    repo_pawns_can_win.print_stats()
    repo_pawns_can_win.print_counts()


repo_pawns_can_win = EvaluationRepository()
