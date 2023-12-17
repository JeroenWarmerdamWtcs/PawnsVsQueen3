# Purpose: basic definitions and functions for the queen versus pawn problem
from typing import *

Square = int  # 0 .. 64
Squares = List[Square]
BoolBoard = List[bool]  # index is Square, value is bool
IntBoard = List[int]  # index is Square, value is int
StrBoard = List[str]  # index is Square, value is str

FILES = list(range(1, 9))
INVALID_FILES = [0, 9]
FILES_PLUS_INVALID_FILES = INVALID_FILES[:1] + FILES + INVALID_FILES[1:]
FILE_NAME = "x" + "abcdefgh" + "x"

RANKS = list(range(1, 9))
INVALID_RANKS = [0, 9]
RANKS_PLUS_INVALID_RANKS = INVALID_RANKS[:1] + RANKS + INVALID_RANKS[1:]
RANK_NAME = "x" + "12345678" + "x"

SQUARES_TO_FILE_AND_RANK = [(0, 0)] + [(f, r) for f in FILES for r in reversed(RANKS)]
# so we start with xx, a8, a7, ..., a1, then b8, b7, ..., h1, etc.
assert len(SQUARES_TO_FILE_AND_RANK) == 1 + 8 * 8
assert SQUARES_TO_FILE_AND_RANK[1] == (1, 8)
SQUARE_TO_FILE = [pair[0] for pair in SQUARES_TO_FILE_AND_RANK]
SQUARE_TO_RANK = [pair[1] for pair in SQUARES_TO_FILE_AND_RANK]

SQUARES = list(range(1, 65))
INVALID_SQUARE = 0
SQUARES_PLUS_INVALID_SQUARE = [INVALID_SQUARE] + SQUARES
SQUARE_NAME = ([FILE_NAME[pair[0]] + RANK_NAME[pair[1]] for pair in SQUARES_TO_FILE_AND_RANK])

assert SQUARE_NAME[1] == "a8"
assert SQUARE_NAME[2] == "a7"
assert SQUARE_NAME[64] == "h1"
assert SQUARE_NAME[INVALID_SQUARE] == "xx"

FILE_RANK_TO_SQUARE = [[next((sq for sq in SQUARES_PLUS_INVALID_SQUARE
                              if SQUARE_TO_FILE[sq] == f and SQUARE_TO_RANK[sq] == r),
                             INVALID_SQUARE)
                        for r in RANKS_PLUS_INVALID_RANKS]
                       for f in FILES_PLUS_INVALID_FILES]

SQ = {SQUARE_NAME[sq]: sq for sq in SQUARES_PLUS_INVALID_SQUARE}

assert SQUARE_NAME[FILE_RANK_TO_SQUARE[1][1]] == "a1"
assert SQUARE_NAME[FILE_RANK_TO_SQUARE[1][8]] == "a8"
assert FILE_RANK_TO_SQUARE[9][1] == INVALID_SQUARE
assert FILE_RANK_TO_SQUARE[INVALID_FILES[0]][3] == INVALID_SQUARE
assert FILE_RANK_TO_SQUARE[4][INVALID_RANKS[1]] == INVALID_SQUARE


def _test_mappings():
    for sq in SQUARES_PLUS_INVALID_SQUARE:
        assert FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq]][SQUARE_TO_RANK[sq]] == sq
    for f in FILES_PLUS_INVALID_FILES:
        for r in RANKS_PLUS_INVALID_RANKS:
            if f in INVALID_FILES or r in INVALID_RANKS:
                assert SQUARE_TO_FILE[FILE_RANK_TO_SQUARE[f][r]] == INVALID_FILES[0]
                assert SQUARE_TO_FILE[FILE_RANK_TO_SQUARE[f][r]] == INVALID_RANKS[0]
            else:
                assert SQUARE_TO_FILE[FILE_RANK_TO_SQUARE[f][r]] == f
                assert SQUARE_TO_RANK[FILE_RANK_TO_SQUARE[f][r]] == r


IS_PROMOTION_SQUARE: BoolBoard = [SQUARE_TO_RANK[sq] == 8 for sq in SQUARES_PLUS_INVALID_SQUARE]


def _str_to_squares(s: str) -> List[Square]:
    result = [SQ[s[i:i + 2]] for i in range(0, len(s), 2)]
    return sorted(result)


assert _str_to_squares("b2g2a8") == [1, 15, 55]
assert _str_to_squares("") == []


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


N = [INVALID_SQUARE] + [FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq] + 0][SQUARE_TO_RANK[sq] + 1] for sq in SQUARES]
NE = [INVALID_SQUARE] + [FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq] + 1][SQUARE_TO_RANK[sq] + 1] for sq in SQUARES]
E = [INVALID_SQUARE] + [FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq] + 1][SQUARE_TO_RANK[sq] + 0] for sq in SQUARES]
SE = [INVALID_SQUARE] + [FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq] + 1][SQUARE_TO_RANK[sq] - 1] for sq in SQUARES]
S = [INVALID_SQUARE] + [FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq] + 0][SQUARE_TO_RANK[sq] - 1] for sq in SQUARES]
SW = [INVALID_SQUARE] + [FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq] - 1][SQUARE_TO_RANK[sq] - 1] for sq in SQUARES]
W = [INVALID_SQUARE] + [FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq] - 1][SQUARE_TO_RANK[sq] + 0] for sq in SQUARES]
NW = [INVALID_SQUARE] + [FILE_RANK_TO_SQUARE[SQUARE_TO_FILE[sq] - 1][SQUARE_TO_RANK[sq] + 1] for sq in SQUARES]
NEXT_SQUARE = {"N": N, "NE": NE, "E": E, "SE": SE, "S": S, "SW": SW, "W": W, "NW": NW}

assert SQUARE_NAME[N[SQ["d4"]]] == "d5"
assert SQUARE_NAME[NEXT_SQUARE["NE"][SQ["d4"]]] == "e5"


def _print_next_square(ns: Dict[str, Squares]) -> None:
    for k, v in ns.items():
        print_board(f"direction {k}", [SQUARE_NAME[v[sq]] for sq in SQUARES_PLUS_INVALID_SQUARE])


def _squares_in_direction(sq: Square, d: Squares) -> Generator[Square, None, None]:
    sq = d[sq]
    while sq != INVALID_SQUARE:
        yield sq
        sq = d[sq]


def _create_direction() -> Dict[Tuple[Square, Square], Optional[str]]:
    result = {(sq1, sq2): None for sq1 in SQUARES for sq2 in SQUARES}
    for sq1 in SQUARES:
        for d, v in NEXT_SQUARE.items():
            for sq2 in _squares_in_direction(sq1, v):
                result[(sq1, sq2)] = d
    return result


DIRECTION = _create_direction()
assert DIRECTION[SQ["d4"], SQ["g1"]] == "SE"
assert DIRECTION[SQ["d4"], SQ["h1"]] is None

HORIZONTAL_RAYS = [[sq1] + list(_squares_in_direction(sq1, NEXT_SQUARE["E"]))
                   for sq1 in SQUARES if SQUARE_TO_FILE[sq1] == 1]
VERTICAL_RAYS = [[sq1] + list(_squares_in_direction(sq1, NEXT_SQUARE["N"]))
                 for sq1 in SQUARES if SQUARE_TO_RANK[sq1] == 1]
DIAGONAL_RAYS = [[sq2] + list(_squares_in_direction(sq2, NEXT_SQUARE["NE"]))
                 for sq2 in SQUARES if SQUARE_TO_FILE[sq2] == 1 or SQUARE_TO_RANK[sq2] == 1]
ANTI_DIAGONAL_RAYS = [[sq2] + list(_squares_in_direction(sq2, NEXT_SQUARE["SE"]))
                      for sq2 in SQUARES if SQUARE_TO_FILE[sq2] == 1 or SQUARE_TO_RANK[sq2] == 8]
DIAGONAL_RAYS = [ray for ray in DIAGONAL_RAYS if len(ray) != 1]
ANTI_DIAGONAL_RAYS = [ray for ray in ANTI_DIAGONAL_RAYS if len(ray) != 1]
RAYS = HORIZONTAL_RAYS + VERTICAL_RAYS + DIAGONAL_RAYS + ANTI_DIAGONAL_RAYS


# Hier de goed plek. Uitleggen waarom dit hier staat. JWA
MAX_INDEX = 64 * 6 ** 8 - 1
FACTOR = [0] + [64 * 6 ** i for i in range(8)]  # used to calculate index of a position
PAWN_FACTOR = [0] + [FACTOR[SQUARE_TO_FILE[sq]] * (SQUARE_TO_RANK[sq] - 1) for sq in SQUARES]


class Pawns:
    def __init__(self, pawns: Squares):
        self.squares = pawns
        self.occupy = [False for _ in SQUARES_PLUS_INVALID_SQUARE]
        self.attack = [0 for _ in SQUARES_PLUS_INVALID_SQUARE]
        for pawn in self.squares:
            self.occupy[pawn] = True
            self.attack[NW[pawn]] += 1
            self.attack[NE[pawn]] += 1
        self.idx = sum(PAWN_FACTOR[sq] for sq in self.squares)

    def __str__(self):
        return "".join([SQUARE_NAME[sq] for sq in self.squares])

    def __repr__(self):
        return str(self)

    def add(self, square):
        self.occupy[square] = True
        self.attack[NW[square]] += 1
        self.attack[NE[square]] += 1
        self.squares.append(square)
        self.squares.sort()  # not necessary, but makes debugging easier  jwa??
        self.idx += PAWN_FACTOR[square]

    def remove(self, pawn):
        assert self.occupy[pawn], self
        self.idx -= PAWN_FACTOR[pawn]
        self.squares.remove(pawn)
        self.attack[NE[pawn]] -= 1
        self.attack[NW[pawn]] -= 1
        self.occupy[pawn] = False

    def move(self, o, d):
        # Faster than remove and add
        self.squares[self.squares.index(o)] = d
        self.occupy[d] = True
        self.occupy[o] = False
        self.attack[NW[o]] -= 1
        self.attack[NE[o]] -= 1
        self.attack[NW[d]] += 1
        self.attack[NE[d]] += 1
        self.idx += PAWN_FACTOR[d] - PAWN_FACTOR[o]

    def get_moves(self):
        result = []
        for pawn in self.squares:
            destination = N[pawn]
            result.append((pawn, destination))
            if SQUARE_TO_RANK[pawn] == 2:
                destination = N[destination]
                result.append((pawn, destination))
        return result


class Position:
    def __init__(self, pawns: Pawns, queen: Square):
        self.pawns = pawns
        self.queen = queen
        self.history = []

    def __str__(self):
        return f"{self.pawns}Q{SQUARE_NAME[self.queen]}"

    def __repr__(self):
        return str(self)

    @property
    def idx(self):
        if self.pawns.idx + self.queen - 1 > MAX_INDEX:
            print(self)
        return self.pawns.idx + self.queen - 1

    def play_queen(self, d):
        self.history.append(self.queen)
        self.queen = d
        self.history.append(d)
        if self.pawns.occupy[d]:
            self.pawns.remove(d)
            self.history.append(True)
        else:
            self.history.append(False)

    def play_pawn(self, o, d):
        self.pawns.move(o, d)
        self.history.append(o)
        self.history.append(d)

    def play_back_queen(self):
        capture = self.history.pop()
        d = self.history.pop()
        o = self.history.pop()
        assert d == self.queen, f"Moving queen not found: {d}, {self}"
        self.queen = o
        if capture:
            self.pawns.add(d)

    def play_back_pawn(self):
        self.pawns.move(self.history.pop(), self.history.pop())

    def get_str_board(self) -> StrBoard:
        result = ["." for _ in SQUARES_PLUS_INVALID_SQUARE]
        result[self.queen] = "q"
        for pawn in self.pawns.squares:
            result[pawn] = "o"
        return result

    def is_square_attacked_by_pawns(self, square) -> bool:
        return self.pawns.attack[square] > 0

    def is_queen_attacked_by_pawns(self) -> bool:
        return self.is_square_attacked_by_pawns(self.queen)

    def get_pawn_moves(self):
        return [(o, d) for (o, d) in self.pawns.get_moves() if self.queen not in (d, N[o])]
        # Often d == N[o], but not in cases like e2e4.

    def get_queen_destinations(self):
        # excluding attacks by pawns
        for d in NEXT_SQUARE.values():
            for square in _squares_in_direction(self.queen, d):
                if not self.pawns.attack[square]:
                    yield square
                if self.pawns.occupy[square]:
                    break

    def can_queen_move_to(self, square):
        if self.pawns.attack[square]:
            return False
        direction = DIRECTION[(self.queen, square)]
        if direction is None:
            return False
        for sq in _squares_in_direction(self.queen, NEXT_SQUARE[direction]):
            if sq == square:
                return True
            if self.pawns.occupy[sq]:
                return False
        assert False, f"should not happen: {self}, {square}"

    def get_queen_destinations_list(self):
        return list(self.get_queen_destinations())

    # Not used
    def get_queen_origins(self):
        for d in NEXT_SQUARE.values():
            for square in _squares_in_direction(self.queen, d):
                if self.pawns.occupy[square]:
                    break
                yield square


def initial_position() -> Position:
    return Position(Pawns(_str_to_squares("a2b2c2d2e2f2g2h2")), SQ["d8"])


if __name__ == "__main__":
    _test_mappings()
    print_board("name", SQUARE_NAME)
    print_board("file", SQUARE_TO_FILE)
    print_board("rank", SQUARE_TO_RANK)
    print_board("promotion", IS_PROMOTION_SQUARE)
    _print_next_square(NEXT_SQUARE)
