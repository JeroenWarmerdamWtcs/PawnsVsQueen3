from timeit import default_timer as timer

from basics import *
from evaluation_functions import evaluate_pawns, PAWNS_WIN_VALUE
from evaluation_functions import get_ordered_square_list_pawn_destinations_best_first
from evaluation_functions import get_ordered_square_list_queen_destinations_best_first

USE_ORDERED_LISTS = False


def get_eval_pawns_to_play(position, deep):
    # return value, best pawn move (destination square)
    if deep == 0 or len(position.pawns) == 0:
        return evaluate_pawns(position.pawns), None

    best_eval = None
    best_pawn = None
    for new_pawn_square in get_ordered_square_list_pawn_destinations_best_first(position):
        if IS_PROMOTION_SQUARE[new_pawn_square]:
            return PAWNS_WIN_VALUE, new_pawn_square
        val, best_queen = get_eval_queen_to_play(position.get_position_after_pawn_play(new_pawn_square), deep - 1)
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
        val, best_pawn = get_eval_pawns_to_play(position.get_position_after_queen_play(next_queen_square), deep - 1)
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
    result = dict_queen_can_win[position]
    if result is not None:
        return result
    # not found in dict, so we have to calculate it
    result = False  # unless we find a winning move

    assert len(position.pawns) > 0, f"position without pawns is not valid when queen to play: {position}"
    assert position.is_valid_queen_to_play()

    list_queen_destinations = get_ordered_square_list_queen_destinations_best_first(position) \
        if USE_ORDERED_LISTS else position.get_queen_destinations()

    for new_queen_square in list_queen_destinations:
        new_position = position.get_position_after_queen_play(new_queen_square)
        if not pawns_can_win(new_position):
            result = True
            break

    dict_queen_can_win.save(position, result)
    return result


def pawns_can_win(position):
    result = dict_pawns_can_win[position]
    if result is not None:
        return result
    # not found in dict, so we have to calculate it
    result = False  # unless we find a winning move

    list_of_pawn_destinations = get_ordered_square_list_pawn_destinations_best_first(position) \
        if USE_ORDERED_LISTS else position.get_pawn_destinations()

    for new_pawn_square in list_of_pawn_destinations:
        if IS_PROMOTION_SQUARE[new_pawn_square]:
            result = True
            break
        new_position = position.get_position_after_pawn_play(new_pawn_square)
        if not queen_can_win(new_position):
            result = True
            break

    dict_pawns_can_win.save(position, result)
    return result


class EvaluationStore:
    def __init__(self):
        self.store = [{} for _ in range(9)]
        # i.e. store[n] contains positions with n pawns
        self.read_count = 0
        self.write_count = 0

    def save(self, position, evaluation):
        assert isinstance(evaluation, bool)
        n = len(position.pawns)
        code = self.position_to_code(position)
        assert code not in self.store[n], f"position already in store: {position}"
        self.store[n][code] = evaluation
        self.write_count += 1

    def __getitem__(self, position):
        n = len(position.pawns)
        code = self.position_to_code(position)
        self.read_count += 1
        return self.store[n].get(code, None)

    def print_stats(self):
        print(f"  Number of valid position: {sum([len(x) for x in self.store])}")
        for n in range(9):
            if len(self.store[n]) > 0:
                print(f"    Number of valid positions with {n} pawns: {len(self.store[n])}", end=" (")
                print(f"W={list(self.store[n].values()).count(True)}", end=" ")
                print(f"L={list(self.store[n].values()).count(False)})")

    def print_counts(self):
        print(f"Reads: {self.read_count}\tWrites: {self.write_count}")

    @staticmethod
    def position_to_code(position):
        return tuple(position.pawns + [position.queen])


def generate_and_evaluate_all_positions_without_pawns():
    for queen in SQUARES:
        assert not pawns_can_win(Position([], queen))
        # without pawns, the latest move was a capture by the queen so pawns needs to play, so
        # assert queen_can_win(([], queen)) is not valid


def generate_and_evaluate_all_positions_with_one_pawn():
    for pawn in PAWN_SQUARES:
        for queen in SQUARES:
            p = Position([pawn], queen)
            if p.is_valid_pawns_to_play():
                pawns_can_win(p)
            if p.is_valid_queen_to_play():
                queen_can_win(p)


def generate_and_evaluate_all_positions_with_two_pawns():
    for pawn1 in PAWN_SQUARES:
        for pawn2 in PAWN_SQUARES:
            if SQUARE_TO_FILE[pawn1] < SQUARE_TO_FILE[pawn2]:
                for queen in SQUARES:
                    p = Position([pawn1, pawn2], queen)
                    if p.is_valid_pawns_to_play():
                        pawns_can_win(p)
                    if p.is_valid_queen_to_play():
                        queen_can_win(p)


def generate_and_evaluate_all_positions_with_three_pawns():
    for pawn1 in PAWN_SQUARES:
        for pawn2 in PAWN_SQUARES:
            if SQUARE_TO_FILE[pawn1] < SQUARE_TO_FILE[pawn2]:
                for pawn3 in PAWN_SQUARES:
                    if SQUARE_TO_FILE[pawn2] < SQUARE_TO_FILE[pawn3]:
                        for queen in SQUARES:
                            p = Position([pawn1, pawn2, pawn3], queen)
                            if p.is_valid_pawns_to_play():
                                pawns_can_win(p)
                            if p.is_valid_queen_to_play():
                                queen_can_win(p)


def print_stats():
    dict_pawns_can_win.print_stats()
    dict_queen_can_win.print_stats()
    dict_pawns_can_win.print_counts()
    dict_queen_can_win.print_counts()


def generate_and_evaluate():
    generate_and_evaluate_all_positions_without_pawns()
    print_stats()
    assert len(dict_pawns_can_win.store[0]) == 64, len(dict_pawns_can_win.store[0])
    generate_and_evaluate_all_positions_with_one_pawn()
    print_stats()
    # pawns to play:
    #  6 + 6 rook pawns each with 62 queen positions
    #  6 * 6 other pawns each with 61 queen positions
    # so 2 * 6 * 62 + 6 * 6 * 61
    assert len(dict_pawns_can_win.store[1]) == 2 * 6 * 62 + 6 * 6 * 61
    # queen to play:
    #  8 * 6 pawn positions and 63 queen position
    # no pawns: 64
    assert len(dict_queen_can_win.store[1]) == 8 * 6 * 63
    print_stats()
    generate_and_evaluate_all_positions_with_two_pawns()
    print_stats()
    # generate_and_evaluate_all_positions_with_three_pawns()
    # evaluation_store.print_stats()


def unit_test():
    p = Position("Qd5")
    assert not pawns_can_win(p)
    dict_pawns_can_win.print_counts()
    dict_queen_can_win.print_counts()

    p = Position("b8Qb3")
    assert not p.is_valid_queen_to_play()
    dict_pawns_can_win.print_counts()
    dict_queen_can_win.print_counts()

    p = Position("b7Qd8")
    assert pawns_can_win(p)
    dict_pawns_can_win.print_counts()
    dict_queen_can_win.print_counts()

    p = Position("b7Qb8")
    assert not pawns_can_win(p)  # Draw
    dict_pawns_can_win.print_counts()
    dict_queen_can_win.print_counts()

    p = Position("b6Qb8")
    assert queen_can_win(p)
    dict_pawns_can_win.print_counts()
    dict_queen_can_win.print_counts()


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
dict_pawns_can_win = EvaluationStore()
dict_queen_can_win = EvaluationStore()
# unit_test()
generate_and_evaluate()
end = timer()
print(end - start)
# main()
