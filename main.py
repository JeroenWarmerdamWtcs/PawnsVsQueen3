import time
from timeit import default_timer as timer

from evaluation import update_if_queen_can_capture_pawn_on_rank7, update_if_queen_can_blocks_pawn_on_rank_7
from evaluation_repository import *
from generator import generate_pawns_with_rank_below_7


def set_evaluation_all_positions_without_pawns_to_queen_has_won():
    for queen in SQUARES:
        repo_pawns_can_win.store(Position(Pawns([]), queen), QUEEN_HAS_WON)


def get_eval_board_pawn_on_rank7(pawns, move) -> bytearray:
    # Returns the evaluation of the position after the move.
    # The pawn move and the queen move are not counted in the values.
    # The returned values for occupied or attacked squares are not used.
    result = bytearray([PAWNS_WIN_IN_1] * len(SQUARES_PLUS_INVALID_SQUARE))
    # If the queen cannot capture the pawn nor block, then the pawn will promote next move
    update_if_queen_can_blocks_pawn_on_rank_7(pawns, move, result)
    update_if_queen_can_capture_pawn_on_rank7(pawns, move, result)
    # If the queen can both capture and block the pawn on rank 7,
    # then the queen must be on rank 7 as well next to the pawn.
    # So that queen square was attacked and the return value will not be used.
    return result


def update_queen_board_along_ray(ray, pawns, queen_board_values_white_to_play, queen_board_value_black_to_play):
    # updates queen_board_values_black_to_play

    # print(pawns, end="\t")
    # for i, sq in enumerate(ray):
    #     print(f"{'*' if pawns.occupy[sq] else ''}{value_to_str(queen_board_values_white_to_play[sq])}", end=" ")
    # print("\t", end="")
    # for i, sq in enumerate(ray):
    #     print(f"{'*' if pawns.occupy[sq] else ''}{value_to_str(queen_board_value_black_to_play[sq])}", end=" ")

    best_value = PAWNS_WIN_IN_1
    index_best_value = 0
    second_value = PAWNS_WIN_IN_1
    index_write = 0
    for i, sq in enumerate(ray):
        value_i = queen_board_values_white_to_play[sq]
        if value_i < best_value:
            second_value = best_value
            best_value = value_i
            index_best_value = i
        elif value_i < second_value:
            second_value = value_i

        if pawns.occupy[sq]:
            for index_write in range(index_write, i):
                value = best_value if index_write != index_best_value else second_value
                sq = ray[index_write]
                if value < queen_board_value_black_to_play[sq]:
                    queen_board_value_black_to_play[sq] = value
            index_write = i + 1
            best_value = value_i
            index_best_value = i  # that is a bit strange as we might set this value
            second_value = PAWNS_WIN_IN_1

    for index_write in range(index_write, len(ray)):
        value = best_value if index_write != index_best_value else second_value
        sq = ray[index_write]
        if value < queen_board_value_black_to_play[sq]:
            queen_board_value_black_to_play[sq] = value
        # queen_board_value_black_to_play[sq] = min(queen_board_value_black_to_play[sq], value)

    # print("\t", end="")
    # for i, sq in enumerate(ray):
    #     print(f"{'*' if pawns.occupy[sq] else ''}{value_to_str(queen_board_value_black_to_play[sq])}", end=" ")
    # print()


def get_eval_board_pawns_below_rank7(pawns) -> bytearray:
    result = bytearray([PAWNS_HAVE_WON] * len(SQUARES_PLUS_INVALID_SQUARE))
    eval_after_queen_move = repo_pawns_can_win.get_eval_board(pawns)
    for ray in RAYS:
        update_queen_board_along_ray(ray, pawns, eval_after_queen_move, result)
    return result


def evaluate_pawns(pawns):
    next_evaluation = {}
    for o, d in pawns.get_moves():
        if SQUARE_TO_RANK[d] == 7:
            next_evaluation[(o, d)] = get_eval_board_pawn_on_rank7(pawns, (o, d))
            # print_board(f"{pawns}, {d}", [value_to_str(v) for v in next_evaluation[(o, d)]])
        else:
            pawns.move(o, d)
            next_evaluation[(o, d)] = get_eval_board_pawns_below_rank7(pawns)
            # print_board(f"{pawns}, {d}", [value_to_str(v) for v in next_evaluation[(o, d)]])
            pawns.move(d, o)

    eval_board = bytearray([QUEEN_HAS_WON] * len(SQUARES_PLUS_INVALID_SQUARE))
    for queen in SQUARES:
        if pawns.occupy[queen]:
            pawns.remove(queen)
            eval_board[queen] = repo_pawns_can_win[Position(pawns, queen)]
            pawns.add(queen)
        elif pawns.attack[queen]:
            eval_board[queen] = PAWNS_WIN_IN_1
        else:
            move_found = False
            for o, d in pawns.get_moves():
                if d != queen and N[o] != queen:
                    move_found = True
                    value = next_evaluation[(o, d)][queen]
                    if value > eval_board[queen]:
                        eval_board[queen] = value
            if move_found:
                eval_board[queen] = add_one_move(eval_board[queen])
            else:
                eval_board[queen] = DRAW

    repo_pawns_can_win.store_eval_board(pawns, eval_board)


def generate_and_evaluate_all_positions_with_fixed_number_of_pawns(nb_pawns):
    for pawns in generate_pawns_with_rank_below_7(nb_pawns):
        evaluate_pawns(pawns)


def generate_and_evaluate():
    set_evaluation_all_positions_without_pawns_to_queen_has_won()
    for nb_pawns in range(1, 9):
        print(nb_pawns)
        generate_and_evaluate_all_positions_with_fixed_number_of_pawns(nb_pawns)


start = timer()
start_cpu = time.process_time()
generate_and_evaluate()
print("saving")
repo_pawns_can_win.save_to_file("repo_pawns_can_win2.bin")
# repo_pawns_can_win.load_from_file("repo_pawns_can_win.bin")
print_repo_stats()
print(f"{initial_position()}: {value_to_str(repo_pawns_can_win[initial_position()])}")

end = timer()
end_cpu = time.process_time()
print(f"time: {end - start:.2f}s")
print(f"cpu time: {end_cpu - start_cpu:.2f}s")
