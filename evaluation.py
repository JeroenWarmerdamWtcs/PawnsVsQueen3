from evaluation_functions import *
from evaluation_repository import repo_queen_can_win, repo_pawns_can_win

USE_ORDERED_LISTS = False  # True is still much slower


def get_eval_pawns_to_play(position, deep):
    # return value, best pawn move (destination square)
    if deep == 0 or len(position.pawns) == 0:
        return evaluate_pawns(position.pawns), None

    best_eval = None
    best_pawn = None
    for new_pawn_square in get_ordered_square_list_pawn_destinations_best_first(position):
        if IS_PROMOTION_SQUARE[new_pawn_square]:
            return PAWNS_WIN_VALUE, new_pawn_square
        new_position = position.copy()
        new_position.play_pawn(new_pawn_square)
        val, best_queen = get_eval_queen_to_play(new_position, deep - 1)
        if best_eval is None or val > best_eval:
            best_eval = val
            best_pawn = new_pawn_square
    return best_eval, best_pawn


def get_eval_queen_to_play(position, deep):
    # return value, best queen move (destination square)
    if deep == 0:
        return evaluate_pawns(position.
                              pawns), None

    best_eval = None
    best_queen = None
    # noinspection SpellCheckingInspection
    for next_queen_square in get_ordered_square_list_queen_destinations_best_first(position):
        # JWA
        # deep == 1 heeft geen zin, alle eval zijn gelijk
        # tenzij er geslagen wordt. Maar heeft get_ordered_square_list_queen_destinations_best_first dan niet al de
        # capture op de eerste plek gezet.
        new_position = position.copy()
        new_position.play_queen(next_queen_square)
        val, best_pawn = get_eval_pawns_to_play(new_position, deep - 1)
        if best_eval is None or val < best_eval:
            best_eval = val
            best_queen = next_queen_square
    return best_eval, best_queen


# queen_can_win and pawns_can_win are mutually recursive
# how do the determine win "by definition"?
# - when a pawn can promote, pawns_can_win will return True
# - when there are no pawns left, pawns_can_win will return False
# - so if the queen wins the last pawn, queen_can_win will return True as
#   the next call of pawns_can_win will return False


def queen_can_win(position):
    result = repo_queen_can_win[position]
    if result is not None:
        return result
    # not found in dict, so we have to calculate it
    result = False  # unless we find a winning move

    assert len(position.pawns) > 0, f"position without pawns is not valid when queen to play: {position}"
    assert position.is_valid_queen_to_play()

    list_queen_destinations = get_ordered_square_list_queen_destinations_best_first(position) \
        if USE_ORDERED_LISTS else position.get_queen_destinations_list()

    queen = position.queen
    for new_queen_square in list_queen_destinations:
        is_capture = new_queen_square in position.pawns
        if is_capture:
            index = position.pawns.index(new_queen_square)
            position.play_queen(new_queen_square)
            result = not pawns_can_win(position)
            position.pawns.insert(index, new_queen_square)  # this might change the order of the pawns
        else:
            position.play_queen(new_queen_square)
            result = not pawns_can_win(position)
        if result:
            break
        # we do not need to restore the queen in between queen moves
    position.queen = queen

    repo_queen_can_win.save(position, result)
    return result


def pawns_can_win(position):
    result = repo_pawns_can_win[position]
    if result is not None:
        return result
    # not found in dict, so we have to calculate it
    result = False  # unless we find a winning move

    list_of_pawn_destinations = get_ordered_square_list_pawn_destinations_best_first(position) \
        if USE_ORDERED_LISTS else position.get_pawn_destinations_list()

    for new_pawn_square in list_of_pawn_destinations:
        if IS_PROMOTION_SQUARE[new_pawn_square]:
            result = True
            break
        new_position = position.copy()
        new_position.play_pawn(new_pawn_square)
        if not queen_can_win(new_position):
            result = True
            break

    repo_pawns_can_win.save(position, result)
    return result
