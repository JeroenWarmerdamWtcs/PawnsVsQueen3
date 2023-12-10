from basics import *


RANK_VALUE = [0, 0, 1, 4, 9, 16, 25, 36, 10 ** 10]
SQUARE_VALUE = [RANK_VALUE[SQUARE_TO_RANK[sq]] for sq in SQUARES_PLUS_INVALID_SQUARE]
MULTIPLIER_RANK_VALUE = [4 ** r for r in RANKS_PLUS_INVALID_RANK]
MULTIPLIER_SQUARE_VALUE = [MULTIPLIER_RANK_VALUE[SQUARE_TO_RANK[sq]] for sq in SQUARES_PLUS_INVALID_SQUARE]

PAWNS_WIN_VALUE = 10 ** 10


def evaluate_pawns(pawns: Pawns) -> int:
    if any([IS_PROMOTION_SQUARE[pawn] for pawn in pawns]):
        return PAWNS_WIN_VALUE

    result = sum(SQUARE_VALUE[pawn] for pawn in pawns)
    n = 1
    latest_file = -1
    for pawn in pawns:
        current_file = SQUARE_TO_FILE[pawn]
        if latest_file + 1 == current_file:
            n += 2
        else:
            n = 1
        result += n
        latest_file = current_file
    return result


assert evaluate_pawns(str_to_squares('a2b2c2d2e2f2g2h2')) == 72
assert evaluate_pawns(str_to_squares('a3b2c2d2e2f2g2h2')) == 75
assert evaluate_pawns(str_to_squares('a3b2')) == 9
assert evaluate_pawns(str_to_squares('a3c2')) == 7


def get_int_board_value_for_a_queen(p: Position) -> IntBoard:
    attacked_squares = p.get_bool_board_attacked_by_pawns()
    result = [0] * len(SQUARES_PLUS_INVALID_SQUARE)

    for pawn in p.pawns:
        # actual position
        multiplier = MULTIPLIER_SQUARE_VALUE[pawn] * (1 if attacked_squares[pawn] else 2)
        result[pawn] += 50 * multiplier
        for d in Direction:
            square = NEXT_SQUARE[pawn][d]
            while square != INVALID_SQUARE:
                result[square] += 3 * multiplier
                square = NEXT_SQUARE[square][d]

        # where pawn could go
        in_front: int = NEXT_SQUARE[pawn][Direction.N]
        if in_front == INVALID_SQUARE or IS_PROMOTION_SQUARE[in_front]:
            continue
        multiplier = MULTIPLIER_SQUARE_VALUE[pawn] * (1 if attacked_squares[in_front] else 2)
        result[in_front] += 8 * multiplier
        for d in Direction:
            square = NEXT_SQUARE[in_front][d]
            while square != INVALID_SQUARE:
                result[square] += 2 * multiplier
                square = NEXT_SQUARE[square][d]

        in_front = NEXT_SQUARE[in_front][Direction.N]
        if in_front == INVALID_SQUARE or IS_PROMOTION_SQUARE[in_front]:
            continue
        result[in_front] += 6 * multiplier
        for d in Direction:
            square = NEXT_SQUARE[in_front][d]
            while square != INVALID_SQUARE:
                result[square] += multiplier
                square = NEXT_SQUARE[square][d]

    return result


def get_ordered_square_list_queen_destinations_best_first(position: Position) -> List[Square]:
    board = get_int_board_value_for_a_queen(position)
    return list(sorted(position.get_queen_destinations_list(), key=lambda square: board[square], reverse=True))


def get_ordered_square_list_pawn_destinations_best_first(position: Position):
    # we try each pawn move. After each pawn move we do the best queen move (from queen perspective).
    # next we evaluate the pawns as they stand after the queen move.
    values = []
    for new_pawn_square in position.get_pawn_destinations_list():
        if IS_PROMOTION_SQUARE[new_pawn_square]:
            return [new_pawn_square]
        next_position = position.copy()
        next_position.play_pawn(new_pawn_square)
        # check if queen can capture
        next_queen_square = get_ordered_square_list_queen_destinations_best_first(next_position)[0]
        next_next_position = next_position.get_position_after_queen_play(next_queen_square)
        values.append((evaluate_pawns(next_next_position.squares), new_pawn_square))

    return list(zip(*values))[1] if values else []
    # sorted version? return list(zip(*sorted(values)))[1] if values else []


def debug_print() -> None:
    p = initial_position()
    print_board("eval queen squares", get_int_board_value_for_a_queen(p))
    print_board("attacked", Position("a3b2c2d2e2f2g2h2Qd8").get_bool_board_attacked_by_pawns())

    p = Position("a6b2c2d2e2f2g2h2Qd2")

    print_board("eval queen squares", get_int_board_value_for_a_queen(p))

    board = ["o" if value else "." for value in p.get_bool_board_occupied()]
    board[p.queen] = "q"

    for i, sq in enumerate(get_ordered_square_list_queen_destinations_best_first(p)):
        board[sq] = str(i + 1)
    print_board("", board)


if __name__ == "__main__":
    print_board("queen int", get_int_board_value_for_a_queen(Position("a5f6h4Qh1")))
    print(get_ordered_square_list_queen_destinations_best_first(Position("a5f6h4Qd3")))
    debug_print()
