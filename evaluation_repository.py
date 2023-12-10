from basics import *
from evaluation_values import *


class EvaluationRepository:
    def __init__(self):
        self.store = bytearray(MAX_INDEX + 1)  # will be initialized to UNKNOWN
        self.read_count = 0
        self.write_count = 0

    def save(self, position, evaluation):
        self.store[position.idx] = evaluation
        self.write_count += 1

    def __getitem__(self, position):
        # code = self.position_to_code(position)
        self.read_count += 1
        return self.store[position.idx]

    def print_stats(self):
        print(f"Number of positions in store: {len(self.store)}")
        print(f"  Number of unknown position: {self.store.count(UNKNOWN)}")
        print(f"  Number of positions with queen win in 1 move: {self.store.count(QUEEN_HAS_WON)}")
        for c, v in enumerate(self.store):
            if v == PAWNS_WIN_IN_2 and False:
                print(self.code_to_position(c))
        print(f"  Number of positions with queen win in 2 moves: {self.store.count(QUEEN_WINS_IN_1)}")
        print(f"  Number of positions with queen win in 3 moves: {self.store.count(QUEEN_WINS_IN_2)}")
        print(f"  Number of positions with queen win in 4 moves: {self.store.count(QUEEN_WINS_IN_3)}")
        print(f"  Number of positions with draw: {self.store.count(DRAW)}")
        print(f"  Number of positions with pawns win in 1 move: {self.store.count(PAWNS_WIN_IN_1)}")
        print(f"  Number of positions with pawns win in 2 moves: {self.store.count(PAWNS_WIN_IN_2)}")
        print(f"  Number of positions with pawns win in 3 moves: {self.store.count(PAWNS_WIN_IN_3)}")

    def print_counts(self):
        print(f"Reads: {self.read_count}\tWrites: {self.write_count}")

    @staticmethod
    def position_to_code(position):
        result = 0
        for pawn in position.squares:
            f, r = SQUARES_TO_FILE_AND_RANK[pawn]
            assert r < 7, position
            result += FACTOR[f] * (r - 1)
        result += position.queen - 1
        return result

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
        return Position(pawns, queen)


def print_repo_stats():
    repo_pawns_can_win.print_stats()
    repo_pawns_can_win.print_counts()


repo_pawns_can_win = EvaluationRepository()


def test():
    assert EvaluationRepository.position_to_code(EvaluationRepository.code_to_position(64)) == 64
    for c in range(10000):
        assert EvaluationRepository.position_to_code(EvaluationRepository.code_to_position(c)) == c, c


if __name__ == "__main__":
    test()
