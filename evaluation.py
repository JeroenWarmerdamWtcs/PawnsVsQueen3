# from evaluation_functions import MULTIPLIER_SQUARE_VALUE, evaluate_pawns
from evaluation_repository import *

USE_ORDERED_LISTS = False  # True is still much slower


def get_pawn_on_rank(pawns, rank):
    for pawn in pawns:
        if SQUARE_TO_RANK[pawn] == rank:
            return pawn
    else:
        assert False


def get_queen_board_value_white_to_play_pawn_on_rank7(queen_board_value_black_to_play) -> IntBoard:
    # not implemented
    return [0] * len(SQUARES_PLUS_INVALID_SQUARE)


def get_queen_origins(position, exclude_squares) -> List[Square]:
    queen_origins = position.get_queen_destinations_list()
    # We turned it around: to what squares can we move from pawn_square.
    # Now we need to check if the queen on such a position is valid IF QUEEN TO PLAY,
    # i.e. not attacked by pawns or on top of a pawn.
    bool_board_attacked_by_pawns = position.get_bool_board_attacked_by_pawns()
    queen_origins = [sq for sq in queen_origins if
                     not position.occupy[sq] and
                     not bool_board_attacked_by_pawns[sq] and
                     sq not in exclude_squares]
    return queen_origins


def update_queen_can_capture_pawn_on_rank7(lower_pawns, pawn_square,
                                           queen_board_value_black_to_play):
    # update queen_board_value_black_to_play
    position_after_queen_captures_pawn = Position(Pawns(lower_pawns), queen=pawn_square)
    if position_after_queen_captures_pawn.is_queen_attacked_by_pawns():
        return  # queen can not capture pawn

    result_if_queen_captures_pawn = evaluate(position_after_queen_captures_pawn)
    queen_origins = get_queen_origins(position_after_queen_captures_pawn,
                                      exclude_squares=
                                      (NEXT_SQUARE[pawn_square][Direction.W],
                                       NEXT_SQUARE[pawn_square][Direction.E])
                                      )
    for queen_square in queen_origins:
        queen_board_value_black_to_play[queen_square] = result_if_queen_captures_pawn


def update_queen_can_blocks_pawn_on_rank_7(lower_pawns, pawn_square, pawns,
                                           queen_board_value_black_to_play):
    # update queen_board_value_black_to_play
    promotion_square = N[pawn_square]
    position_after_queen_blocks = Position(Pawns(pawns), promotion_square)
    queen_origins = get_queen_origins(position_after_queen_blocks,
                                      exclude_squares=(W[pawn_square], E[pawn_square]))

    file = SQUARE_TO_FILE[pawn_square]
    result_if_queen_blocks = (
        DRAW if lower_pawns == [] else
        PAWNS_WIN_IN_2 if any(pawn for pawn in lower_pawns if SQUARE_TO_RANK[pawn] == 6) else
        PAWNS_WIN_IN_2 if (file > 1 and FILE_RANK_TO_SQUARE[file - 1][5] in lower_pawns) else
        PAWNS_WIN_IN_2 if (file < 8 and FILE_RANK_TO_SQUARE[file + 1][5] in lower_pawns) else
        UNKNOWN)
    if result_if_queen_blocks == UNKNOWN:
        #  White has lower pawns, none on rank 6 and none can defend the pawn on rank 7.
        #  So white does the best pawn move and black will capture the pawn on rank 7 next.
        result_if_queen_captures_pawn = QUEEN_HAS_WON  # this value will be overwritten
        p = Position(Pawns(lower_pawns), pawn_square)
        list_of_pawn_moves = p.get_pawn_moves()
        for o, d in list_of_pawn_moves:
            p.play_pawn(o, d)
            # p.play_queen(pawn_square)  we did this move already
            result_if_queen_captures_pawn = max(result_if_queen_captures_pawn,
                                                repo_pawns_can_win[p])
            # p.play_back_queen()
            p.play_back_pawn()

        result_if_queen_blocks = add_one_move(result_if_queen_captures_pawn)

    for queen_square in queen_origins:
        queen_board_value_black_to_play[queen_square] = result_if_queen_blocks


def get_queen_board_value_black_to_play_pawn_on_rank7(pawns) -> IntBoard:
    result = [PAWNS_WIN_IN_1] * len(SQUARES_PLUS_INVALID_SQUARE)
    pawn_square = get_pawn_on_rank(pawns, 7)
    lower_pawns = [p for p in pawns if SQUARE_TO_RANK[p] < 7]

    update_queen_can_capture_pawn_on_rank7(lower_pawns, pawn_square, result)
    update_queen_can_blocks_pawn_on_rank_7(lower_pawns, pawn_square, pawns, result)

    return result


def get_queen_board_value_white_to_play(pawns) -> IntBoard:
    result = [0] * len(SQUARES_PLUS_INVALID_SQUARE)
    for queen in SQUARES:
        if queen not in pawns:
            result[queen] = evaluate(Position(Pawns(pawns), queen))
    return result


def get_queen_board_value(pawns) -> IntBoard:
    #  for each square, we want the evaluation of the position
    #  when the queen is on that square, and it is white to play
    # if pawn on rank 7 or 8
    if any(SQUARE_TO_RANK[pawn] > 6 for pawn in pawns):
        return get_queen_board_value_white_to_play_pawn_on_rank7()

    #  for each square, we want the evaluation of the position
    #  when the has to move from that square
    result = [0] * len(SQUARES_PLUS_INVALID_SQUARE)
    for queen in SQUARES:
        if queen not in pawns:
            result[queen] = evaluate_pawns(pawns, queen)
    return result


def evaluate(position):
    #    if str(position) == "a5b5f3Qh5":
    if str(position) == "a2Qc3":
        jwa = 5

    # white to play, at least one pawn, no pawn on rank 7 or 8
    # list_of_pawn_destinations = get_ordered_square_list_pawn_destinations_best_first(position)
    list_of_pawn_moves = position.get_pawn_moves()

    if len(list_of_pawn_moves) == 0:
        return DRAW

    best_value_for_pawns = 0  # worst case for white
    for o, d in list_of_pawn_moves:
        position.play_pawn(o, d)
        if SQUARE_TO_RANK[d] == 7:  # special case, not in repo
            promotion_square = N[d]
            if position.can_queen_move_to(d):
                # This means d is not defended.
                # The queen can and must capture the pawn on d.
                position.play_queen(d)
                best_value_for_pawns = max(best_value_for_pawns, add_one_move(repo_pawns_can_win[position]))
                position.play_back_queen()

            elif not position.can_queen_move_to(promotion_square):
                position.play_back_pawn()
                return PAWNS_WIN_IN_2

            # queen must move to the promotion square
            elif any(SQUARE_TO_RANK[sq] == 6 for sq in position.pawns.squares):
                best_value_for_pawns = PAWNS_WIN_IN_3
                # White will advance another pawn to rank 7 and one of them promotes.
                # It might be better to advance the other pawn on rank 6, so we so not return yet

            elif position.pawns.attack[o] > 1:
                position.play_back_pawn()
                return PAWNS_WIN_IN_3
                # White will advance the attacking pawn to defend the pawn on d.
                # The queen must leave the promotion square, so the pawn on d will promote.
                # No player can do better.

            else:
                # The queen must block and then capture that pawn on file7.
                position.play_queen(promotion_square)

                # list_of_second_pawn_destinations = get_ordered_square_list_pawn_destinations_best_first(new_position)
                list_of_second_pawn_moves = position.get_pawn_moves()

                if len(list_of_second_pawn_moves) == 0:
                    position.play_back_queen()
                    position.play_back_pawn()
                    return DRAW

                for o2, d2 in list_of_second_pawn_moves:
                    position.play_pawn(o2, d2)
                    position.play_queen(d)  # obligatory and possible
                    best_value_for_pawns = max(best_value_for_pawns,
                                               add_two_moves(repo_pawns_can_win[position]))
                    position.play_back_queen()
                    position.play_back_pawn()

                position.play_back_queen()

        elif best_value_for_pawns < PAWNS_WIN_IN_3:
            if str(position) == "a5b5f3Qh5x":
                for rank in reversed(RANKS):
                    for file in FILES:
                        new_queen = FILE_RANK_TO_SQUARE[file][rank]
                        new_pawns = position.squares.copy()
                        if new_queen in position.squares:
                            new_pawns.remove(new_queen)
                        new_position = Position(Pawns(new_pawns), new_queen)
                        print(f"{value_to_str(repo_pawns_can_win[new_position]):3}", end=" ")
                    print()

                input()
            best_for_queen = PAWNS_WIN_IN_1
            # list_of_queen_destinations = get_ordered_square_list_queen_destinations_best_first(new_position)
            list_of_queen_destinations = position.get_queen_destinations_list()
            for new_queen_square in list_of_queen_destinations:
                position.play_queen(new_queen_square)

                best_for_queen = min(best_for_queen, add_one_move(repo_pawns_can_win[position]))
                position.play_back_queen()
                if best_value_for_pawns >= best_for_queen:
                    break
            best_value_for_pawns = max(best_value_for_pawns, best_for_queen)

        position.play_back_pawn()

    return best_value_for_pawns
