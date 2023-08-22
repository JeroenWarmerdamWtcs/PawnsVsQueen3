from enum import Enum, IntEnum, unique
from typing import *

Square = int  # 0 .. 64
Queen = Square
Pawns = List[Square]  # ordered
BoolBoard = List[bool]  # index is Square, value is bool
IntBoard = List[int]  # index is Square, value is int
StrBoard = List[str]  # index is Square, value is str

FILES = list(range(1, 9))
INVALID_FILE = 0
FILES_PLUS_INVALID_FILE = [INVALID_FILE] + FILES
FILE_NAME = "x" + "abcdefgh"

RANKS = list(range(1, 9))
INVALID_RANK = 0
RANKS_PLUS_INVALID_RANK = [INVALID_RANK] + RANKS
RANK_NAME = "x" + "12345678"

SQUARES_AS_PAIRS = [(f, r) for r in reversed(RANKS) for f in FILES]
# so we start with a8, b8, ..., h8, then a7, b7, ..., h7, etc.
assert len(SQUARES_AS_PAIRS) == 8 * 8

SQUARES = list(range(1, 65))
INVALID_SQUARE = 0
SQUARES_PLUS_INVALID_SQUARE = [INVALID_SQUARE] + SQUARES
SQUARE_NAME = ([FILE_NAME[INVALID_FILE] + RANK_NAME[INVALID_RANK]] +
               [FILE_NAME[pair[0]] + RANK_NAME[pair[1]] for pair in SQUARES_AS_PAIRS])

assert SQUARE_NAME[1] == "a8"
assert SQUARE_NAME[2] == "b8"
assert SQUARE_NAME[64] == "h1"
assert SQUARE_NAME[INVALID_SQUARE] == "xx"

SQUARE_TO_FILE = [INVALID_FILE] + [pair[0] for pair in SQUARES_AS_PAIRS]
SQUARE_TO_RANK = [INVALID_RANK] + [pair[1] for pair in SQUARES_AS_PAIRS]
FILE_RANK_TO_SQUARE = [[next((sq for sq in SQUARES_PLUS_INVALID_SQUARE
                              if SQUARE_TO_FILE[sq] == f and SQUARE_TO_RANK[sq] == r),
                             INVALID_SQUARE)
                        for r in RANKS_PLUS_INVALID_RANK]
                       for f in FILES_PLUS_INVALID_FILE]

# for example FILE_RANK_TO_SQUARE[1][1] is a1, FILE_RANK_TO_SQUARE[1][2] is a2, etc.


def test_mappings():
    for sq in SQUARES_PLUS_INVALID_SQUARE:
        assert FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq]][SQUARE_TO_RANK[sq]] == sq
    for f in FILES_PLUS_INVALID_FILE:
        for r in RANKS_PLUS_INVALID_RANK:
            if f == INVALID_FILE or r == INVALID_RANK:
                assert SQUARE_TO_FILE[FILE_RANK_TO_SQUARE[f][r]] == INVALID_FILE
                assert SQUARE_TO_FILE[FILE_RANK_TO_SQUARE[f][r]] == INVALID_RANK
            else:
                assert SQUARE_TO_FILE[FILE_RANK_TO_SQUARE[f][r]] == f
                assert SQUARE_TO_RANK[FILE_RANK_TO_SQUARE[f][r]] == r


assert SQUARE_NAME[FILE_RANK_TO_SQUARE[1][1]] == "a1"
assert SQUARE_NAME[FILE_RANK_TO_SQUARE[1][2]] == "a2"
assert SQUARE_NAME[FILE_RANK_TO_SQUARE[8][8]] == "h8"
assert FILE_RANK_TO_SQUARE[INVALID_FILE][3] == FILE_RANK_TO_SQUARE[4][INVALID_RANK] == INVALID_SQUARE

PAWN_SQUARES: List[Square] = [sq for sq in SQUARES if 1 < SQUARE_TO_RANK[sq]]
IS_PROMOTION_SQUARE: BoolBoard = [SQUARE_TO_RANK[sq] == 8 for sq in SQUARES_PLUS_INVALID_SQUARE]


def str_to_square(s: str) -> Square:
    return next((sq for sq in SQUARES_PLUS_INVALID_SQUARE if SQUARE_NAME[sq] == s), INVALID_SQUARE)


def squares(s: str) -> List[Square]:
    result = []
    while s != "":
        result.append(str_to_square(s[:2]))
        s = s[2:]
    return sorted(result)


assert str_to_square("b2") == 50, str_to_square("b2")
assert squares("b2g2a8") == [1, 50, 55], squares("b2g2a8")
assert squares("") == []


def print_board(name: str, values: List[any]) -> None:
    assert len(values) == len(SQUARES_PLUS_INVALID_SQUARE)
    cell_width: int = max(2, max(len(str(values[sq])) for sq in SQUARES))
    print()
    print(f"*********  {name}  ********")
    for rank in reversed(RANKS):
        print(RANK_NAME[rank] + " | " + " ".join(
            [f"{values[FILE_RANK_TO_SQUARE[file][rank]]:>{cell_width}}" for file in FILES]))

    print("    " + " ".join(["-" * cell_width] * len(FILES)))
    print("    " + " ".join([FILE_NAME[file] * cell_width for file in FILES]))


@unique
class Direction(IntEnum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7


@unique
class DirectionVector(Enum):
    N = (0, 1)
    NE = (1, 1)
    E = (1, 0)
    SE = (1, -1)
    S = (0, -1)
    SW = (-1, -1)
    W = (-1, 0)
    NW = (-1, 1)


def create_next_square() -> List[List[Square]]:
    # sets result[sq][d] to the square next to sq in direction d
    result = [[INVALID_SQUARE for _ in Direction] for _ in SQUARES_PLUS_INVALID_SQUARE]
    for d in Direction:
        result[INVALID_SQUARE][d] = INVALID_SQUARE
        df, dr = DirectionVector[d.name].value
        for sq in SQUARES:
            f = SQUARE_TO_FILE[sq] + df
            r = SQUARE_TO_RANK[sq] + dr
            result[sq][d] = (FILE_RANK_TO_SQUARE[f][r]
                             if f in FILES_PLUS_INVALID_FILE and r in RANKS_PLUS_INVALID_RANK
                             else INVALID_SQUARE)
    return result


def print_next_square(ns: List[List[Square]]) -> None:
    for d in Direction:
        print_board(d.name, [SQUARE_NAME[ns[sq][d]] for sq in SQUARES_PLUS_INVALID_SQUARE])


NEXT_SQUARE = create_next_square()
assert NEXT_SQUARE[str_to_square("d4")][Direction.NE] == str_to_square("e5")


def get_bool_board_attacked_by_queen(queen) -> BoolBoard:
    # note queen might jump over pawns in this method
    board = [False for _ in SQUARES_PLUS_INVALID_SQUARE]
    for d in Direction:
        square = NEXT_SQUARE[queen][d]
        while square != INVALID_SQUARE:
            board[square] = True
            square = NEXT_SQUARE[square][d]
    return board


class Position:
    def __init__(self, *args):
        # either a string like "b2g2a8Qd4" or a list of pawns and a queen
        if len(args) == 2:
            self.pawns, self.queen = args
        else:
            pawns, queen = args[0].split("Q")
            self.pawns = squares(pawns)
            self.queen = str_to_square(queen)

    def __str__(self):
        return "".join([SQUARE_NAME[pawn] for pawn in self.pawns]) + "Q" + SQUARE_NAME[self.queen]

    def __is_valid(self) -> bool:
        # JWA: why is a position without a pawn valid but a position without a queen not?
        if any(SQUARE_TO_RANK[pawn] in (1, 8) for pawn in self.pawns):
            return False
        if self.queen in self.pawns:
            return False
        return True

    def is_valid_queen_to_play(self) -> bool:
        return self.__is_valid()

    def is_valid_pawns_to_play(self) -> bool:
        if not self.__is_valid():
            return False
        if NEXT_SQUARE[self.queen][Direction.SW] in self.pawns:
            return False
        if NEXT_SQUARE[self.queen][Direction.SE] in self.pawns:
            return False
        return True

    def get_position_after_queen_play(self, new_queen_square):
        new_pawns = self.pawns.copy()
        if new_queen_square in new_pawns:
            new_pawns.remove(new_queen_square)
        return Position(new_pawns, new_queen_square)

    def get_position_after_pawn_play(self, new_pawn_square):
        new_pawns = self.pawns.copy()
        for i, pawn in enumerate(new_pawns):
            if SQUARE_TO_FILE[pawn] == SQUARE_TO_FILE[new_pawn_square]:
                new_pawns[i] = new_pawn_square
                return Position(new_pawns, self.queen)

        assert False, f"Moving pawn not found: {new_pawn_square}, {self.pawns}"

    def get_str_board(self) -> StrBoard:
        result = ["." for _ in SQUARES_PLUS_INVALID_SQUARE]
        result[self.queen] = "q"
        for pawn in self.pawns:
            result[pawn] = "o"
        return result

    def get_bool_board_occupied(self) -> BoolBoard:
        result = [False for _ in SQUARES_PLUS_INVALID_SQUARE]
        result[self.queen] = True
        for pawn in self.pawns:
            result[pawn] = True
        return result

    def get_bool_board_attacked_by_pawns(self) -> BoolBoard:
        board = [False for _ in SQUARES_PLUS_INVALID_SQUARE]
        for pawn in self.pawns:
            for d in [Direction.NW, Direction.NE]:
                board[NEXT_SQUARE[pawn][d]] = True
        return board

    def get_pawn_destinations(self):
        for pawn in self.pawns:
            result = NEXT_SQUARE[pawn][Direction.N]
            if result in (INVALID_SQUARE, self.queen):
                continue
            yield result
            if SQUARE_TO_RANK[pawn] == 2:
                result = NEXT_SQUARE[result][Direction.N]
                if result == self.queen:
                    continue
                yield result

    def get_queen_destinations(self):
        occupied_squares = self.get_bool_board_occupied()
        attacked_squares = self.get_bool_board_attacked_by_pawns()
        for d in Direction:
            square = NEXT_SQUARE[self.queen][d]
            while square != INVALID_SQUARE:
                if not attacked_squares[square]:
                    yield square
                if occupied_squares[square]:
                    break
                square = NEXT_SQUARE[square][d]


def initial_position() -> Position:
    return Position("a2b2c2d2e2f2g2h2Qd8")


if __name__ == "__main__":
    test_mappings()
    print_board("name", SQUARE_NAME)
    print_board("file", SQUARE_TO_FILE)
    print_board("rank", SQUARE_TO_RANK)
    print_board("promotion", IS_PROMOTION_SQUARE)
    print_next_square(NEXT_SQUARE)
