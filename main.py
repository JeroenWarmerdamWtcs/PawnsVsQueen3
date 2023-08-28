import time
from itertools import combinations
from timeit import default_timer as timer

from basics import *
from evaluation import pawns_can_win, queen_can_win, get_eval_pawns_to_play, get_eval_queen_to_play
from evaluation_repository import repo_pawns_can_win, repo_queen_can_win, print_repo_stats
from generator import generate_all_positions_without_pawns, generate_all_positions_with_fixed_number_of_pawns


def generate_and_evaluate_all_positions_without_pawns():
    for p in generate_all_positions_without_pawns():
        assert not pawns_can_win(p)
        # without pawns, the latest move was a capture by the queen so pawns needs to play, so
        # assert pawns_can_win is not valid


def generate_and_evaluate_all_positions_with_fixed_number_of_pawns(nb_pawns):
    for p in generate_all_positions_with_fixed_number_of_pawns(nb_pawns):
        if p.is_valid_pawns_to_play():
            pawns_can_win(p)
        if p.is_valid_queen_to_play():
            queen_can_win(p)


def generate_and_evaluate():
    generate_and_evaluate_all_positions_without_pawns()
    print_repo_stats()
    assert len(repo_pawns_can_win.store[0]) == 64, len(repo_pawns_can_win.store[0])
    generate_and_evaluate_all_positions_with_fixed_number_of_pawns(1)
    print_repo_stats()
    # pawns to play:
    #  6 + 6 rook pawns each with 62 queen positions
    #  6 * 6 other pawns each with 61 queen positions
    # so 2 * 6 * 62 + 6 * 6 * 61
    assert len(repo_pawns_can_win.store[1]) == 2 * 6 * 62 + 6 * 6 * 61
    # queen to play:
    #  8 * 6 pawn positions and 63 queen position
    # no pawns: 64
    assert len(repo_queen_can_win.store[1]) == 8 * 6 * 63
    print_repo_stats()
    generate_and_evaluate_all_positions_with_fixed_number_of_pawns(2)
    print_repo_stats()
    generate_and_evaluate_all_positions_with_fixed_number_of_pawns(3)
    print_repo_stats()


def is_position_where_queen_might_just_have_captured_a_connected_pawns(position):
    if not position.is_valid_pawns_to_play():
        return False
    if SQUARE_TO_RANK[position.queen] in (1, 8):
        return False
    queen_file = SQUARE_TO_FILE[position.queen]
    for pawn in position.pawns:
        if SQUARE_TO_FILE[pawn] in (queen_file - 1, queen_file + 1):
            return True
    return False


def position_is_still_winning_without_one_pawn(position):
    for subset in combinations(position.pawns, len(position.pawns) - 1):
        if pawns_can_win(Position(list(subset), position.queen)):
            return True
    return False


def unit_test():
    p = Position("Qd5")
    assert not pawns_can_win(p)
    repo_pawns_can_win.print_counts()
    repo_queen_can_win.print_counts()

    p = Position("b8Qb3")
    assert not p.is_valid_queen_to_play()
    repo_pawns_can_win.print_counts()
    repo_queen_can_win.print_counts()

    p = Position("b7Qd8")
    assert pawns_can_win(p)
    repo_pawns_can_win.print_counts()
    repo_queen_can_win.print_counts()

    p = Position("b7Qb8")
    assert not pawns_can_win(p)  # Draw
    repo_pawns_can_win.print_counts()
    repo_queen_can_win.print_counts()

    p = Position("b6Qb8")
    assert queen_can_win(p)
    repo_pawns_can_win.print_counts()
    repo_queen_can_win.print_counts()


def main():
    position = initial_position()

    while True:
        val, new_pawn_square = get_eval_pawns_to_play(position, 3)
        if IS_PROMOTION_SQUARE[new_pawn_square]:
            return
        position = position.get_position_after_pawn_play(new_pawn_square)
        print_board(val, position.get_str_board())
        input()
        val, new_queen_square = get_eval_queen_to_play(position, 5)
        position = position.get_position_after_queen_play(new_queen_square)
        print_board(val, position.get_str_board())
        input()


start = timer()
start_cpu = time.process_time()
# unit_test()
generate_and_evaluate()
end = timer()
end_cpu = time.process_time()
print(end - start)
print(end_cpu - start_cpu)
# main()
