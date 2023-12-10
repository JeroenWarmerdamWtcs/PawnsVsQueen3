from itertools import product, combinations
from basics import *


def generate_all_positions_without_pawns():
    for queen in SQUARES:
        yield Position(Pawns([]), queen)


def generate_pawns_with_rank_below_7_in_fixed_files(files):
    start_squares = [FILE_RANK_TO_SQUARE[file][6] for file in files]
    pawns = Pawns(start_squares[:])
    highest_index = len(files) - 1
    index = highest_index
    while True:
        yield pawns
        square = pawns.squares[index]
        while SQUARE_TO_RANK[square] == 2:
            pawns.move(square, start_squares[index])
            if index == 0:
                return
            index -= 1
            square = pawns.squares[index]
        pawns.move(square, S[square])
        index = highest_index

    # for ranks in product([6, 5, 4, 3, 2], repeat=len(files)):
    #     pawns = [FILE_RANK_TO_SQUARE[file][rank] for file, rank in zip(files, ranks)]
    #     yield Pawns(pawns)


def generate_pawns_with_rank_below_7(nb_pawns):
    for files in combinations(FILES, nb_pawns):
        for pawns in generate_pawns_with_rank_below_7_in_fixed_files(files):
            yield pawns


def generate_all_positions_with_fixed_number_of_isolated_pawns(nb_pawns):
    for pre_files in combinations(range(1, 10 - nb_pawns), nb_pawns):
        pawn_files = [pre_file + gap for pre_file, gap in zip(pre_files, range(nb_pawns))]
        for pawns in generate_pawns_with_rank_below_7_in_fixed_files(pawn_files):
            for queen in SQUARES:
                if queen not in pawns:
                    p = Position(pawns, queen)
                    if not p.is_queen_attacked_by_pawns():
                        yield p


def generate_all_positions_with_isolated_pawns():
    for nb_pawns in range(1, 5):
        for p in generate_all_positions_with_fixed_number_of_isolated_pawns(nb_pawns):
            yield p
