import time
from timeit import default_timer as timer

from evaluation import evaluate
from evaluation_repository import *
from generator import generate_pawns_with_rank_below_7

import sys
sys.stdout = open('output.txt', mode='w')


def set_evaluation_all_positions_without_pawns_to_queen_has_won():
    for queen in SQUARES:
        repo_pawns_can_win.save(Position(Pawns([]), queen), QUEEN_HAS_WON)


def generate_and_evaluate_all_positions_with_fixed_number_of_pawns(nb_pawns):
    for pawns in generate_pawns_with_rank_below_7(nb_pawns):
        for queen in SQUARES:
            p = Position(pawns, queen)
            if pawns.occupy[queen]:
                pawns_copy = Pawns(pawns.squares[:])
                pawns_copy.remove(queen)
                p_corrected = Position(pawns_copy, queen)
                repo_pawns_can_win.save(p, repo_pawns_can_win[p_corrected])
            else:
                p = Position(pawns, queen)
                repo_pawns_can_win.save(p, evaluate(p))
                # print(p, evaluate(p), end=" ")
                # print(repo_pawns_can_win[p])
                assert p.pawns == pawns
                assert p.queen == queen
            # assert repo_pawns_can_win[p] == eval_board[queen], \
            #     f"{p}: {value_to_str(repo_pawns_can_win[p])} != {value_to_str(eval_board[queen])}"


def generate_and_evaluate():
    set_evaluation_all_positions_without_pawns_to_queen_has_won()
    generate_and_evaluate_all_positions_with_fixed_number_of_pawns(1)
    print_repo_stats()
    # noinspection SpellCheckingInspection
    assert repo_pawns_can_win.store.count(DRAW) == len([2, 3, 4, 5, 6]) * len("abcdefgh") + \
           len("ah") * 12 + len("bcdefg") * 10
    assert repo_pawns_can_win.store.count(QUEEN_HAS_WON) == 64 + 5 * 8
    # 5 * 8 positions with the queen on top of the pawn
    assert repo_pawns_can_win.store.count(QUEEN_WINS_IN_1) == 726
    assert repo_pawns_can_win.store.count(QUEEN_WINS_IN_2) == 1360
    assert repo_pawns_can_win.store.count(PAWNS_WIN_IN_2) == 240

    generate_and_evaluate_all_positions_with_fixed_number_of_pawns(2)
    print_repo_stats()
    generate_and_evaluate_all_positions_with_fixed_number_of_pawns(3)
    print_repo_stats()
    # cpu time 66.09s
    # cpu time 57.62s


start = timer()
start_cpu = time.process_time()
# unit_test()
generate_and_evaluate()
end = timer()
end_cpu = time.process_time()
print(f"time: {end - start:.2f}s")
print(f"cpu time: {end_cpu - start_cpu:.2f}s")


def print_stats_pawns_below_rank_7_play_and_lose():
    for n in range(9):
        if len(repo_pawns_can_win.store[n]) > 0 and n == 3:  # jwa
            count = {}
            for code, evaluation in repo_pawns_can_win.store[n].items():
                pawns = list(code[:-1])
                pawns.sort(key=SQUARE_TO_FILE.__getitem__)
                files = tuple(SQUARE_TO_FILE[pawn] for pawn in pawns)
                if all(SQUARE_TO_RANK[pawn] < 7 for pawn in code[:-1]) and not evaluation:
                    count[files] = count.get(files, 0) + 1
            for files, count in sorted(count.items(), key=lambda x: x[1]):
                print(f"{files}: {count}")
