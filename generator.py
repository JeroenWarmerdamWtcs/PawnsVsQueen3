from itertools import product, combinations

from basics import *


def generate_all_positions_without_pawns():
    for queen in SQUARES:
        yield Position([], queen)


def generate_all_positions_fixed_pawn_files(files):
    for ranks in product(reversed(PAWN_RANKS), repeat=len(files)):
        pawns = [FILE_RANK_TO_SQUARE[file][rank] for file, rank in zip(files, ranks)]
        for queen in SQUARES:
            yield Position(pawns, queen)


def generate_all_positions_with_fixed_number_of_pawns(nb_pawns):
    for files in combinations(FILES, nb_pawns):
        for p in generate_all_positions_fixed_pawn_files(files):
            yield p


def generate_all_positions_with_fixed_number_of_isolated_pawns(nb_pawns):
    for pre_files in combinations(range(1, 10 - nb_pawns), nb_pawns):
        pawn_files = [pre_file + gap for pre_file, gap in zip(pre_files, range(nb_pawns))]
        for p in generate_all_positions_fixed_pawn_files(pawn_files):
            yield p


def generate_all_positions_with_isolated_pawns():
    for nb_pawns in range(1, 5):
        for p in generate_all_positions_with_fixed_number_of_isolated_pawns(nb_pawns):
            yield p
