from timeit import default_timer as timer

from basics import *
from evaluation_functions import evaluate_pawns
from evaluation_functions import get_ordered_square_list_pawn_destinations_best_first
from evaluation_functions import get_ordered_square_list_queen_destinations_best_first

USE_ORDERED_LISTS = True


def get_eval_pawns_to_play(position, deep):
    pawns, queen = position
    if deep == 0 or pawns_have_lost(pawns):
        return evaluate_pawns(pawns), None

    best_eval = None
    best_pawn = None
    for new_pawn in get_ordered_square_list_pawn_destinations_best_first(position):
        val, best_queen = get_eval_queen_to_play(get_position_after_pawn_play(position, new_pawn), deep - 1)
        if best_eval is None or val > best_eval:
            best_eval = val
            best_pawn = new_pawn
    return best_eval, best_pawn


def get_eval_queen_to_play(position, deep):
    pawns, queen = position
    if deep == 0 or pawns_have_won(pawns):
        return evaluate_pawns(pawns), None

    best_eval = None
    best_queen = None
    # noinspection SpellCheckingInspection
    for next_queen in get_ordered_square_list_queen_destinations_best_first(position):
        # deep == 1 heeft geen zin, alle eval zijn gelijk
        # tenzij er geslagen wordt. Maar heeft get_ordered_square_list_queen_destinations_best_first dan niet al de
        # capture op de eerste plek gezet.
        val, best_pawn = get_eval_pawns_to_play(get_position_after_queen_play(position, next_queen), deep - 1)
        if best_eval is None or val < best_eval:
            best_eval = val
            best_queen = next_queen
    return best_eval, best_queen


def queen_can_win(position):
    result = evaluation_store[position, "BLACK"]
    if result is not None:
        return result == Status.WIN

    if pawns_have_won(position):
        evaluation_store.save(position, "BLACK", Status.LOSE)
        return False

    list_queen_destinations = get_ordered_square_list_queen_destinations_best_first(position) \
        if USE_ORDERED_LISTS else \
        get_queen_destinations(position)
    for new_queen in list_queen_destinations:
        new_position = get_position_after_queen_play(position, new_queen)
        if not pawns_can_win(new_position):
            evaluation_store.save(position, "BLACK", Status.WIN)
            return True

    evaluation_store.save(position, "BLACK", Status.LOSE)
    return False


def pawns_can_win(position):
    result = evaluation_store[(position, "WHITE")]
    if result is not None:
        return result == Status.WIN

    list_of_pawn_destinations = get_ordered_square_list_pawn_destinations_best_first(position) \
        if USE_ORDERED_LISTS else get_pawn_destinations(position)

    for new_pawn in list_of_pawn_destinations:
        new_position = get_position_after_pawn_play(position, new_pawn)
        if not queen_can_win(new_position):
            evaluation_store.save(position, "WHITE", Status.WIN)
            return True

    evaluation_store.save(position, "WHITE", Status.LOSE)
    return False


class Status(IntEnum):
    WIN = 1
    DRAW = 0
    LOSE = -1

    def __str__(self):
        return {Status.WIN: "+", Status.DRAW: '=', Status.LOSE: "-"}[self]


class EvaluationStore:
    def __init__(self):
        self.store = {"WHITE": [{} for _ in range(9)],
                      "BLACK": [{} for _ in range(9)]}
        # i.e. store[p][n] contains positions with n pawns and p to play
        self.read_count = {"WHITE": 0, "BLACK": 0}
        self.write_count = {"WHITE": 0, "BLACK": 0}

    def save(self, position, player, evaluation):
        assert isinstance(evaluation, Status)
        pawns, queen = position
        n = len(pawns)
        code = self.position_to_code(position)
        assert code not in self.store[player][n], f"position already in store: {position}"
        self.store[player][n][code] = evaluation
        self.write_count[player] += 1

    def __getitem__(self, index):
        position, player = index
        pawns, queen = position
        n = len(pawns)
        code = self.position_to_code(position)
        self.read_count[player] += 1
        return self.store[player][n].get(code, None)

    def print_stats(self):
        for p in ("WHITE", "BLACK"):
            print(f"Player: {p}")
            print(f"  Number of valid position: {sum([len(x) for x in self.store[p]])}")
            for n in range(9):
                if len(self.store[p][n]) > 0:
                    print(f"    Number of valid positions with {n} pawns: {len(self.store[p][n])}", end=" (")
                    print(f"W={list(self.store[p][n].values()).count(Status.WIN)}", end=" ")
                    print(f"D={list(self.store[p][n].values()).count(Status.DRAW)}", end=" ")
                    print(f"L={list(self.store[p][n].values()).count(Status.LOSE)})")

        for code in self.store["BLACK"][2]:
            if self.store["BLACK"][2][code] == Status.DRAW:
                print(code)

    def print_counts(self):
        print(f"Reads: {self.read_count}", end="\t")
        print(f"Writes: {self.write_count}")

    @staticmethod
    def position_to_code(position):
        pawns, queen = position
        return tuple(pawns + [queen])


def generate_and_evaluate_all_positions_without_pawns():
    for queen in SQUARES:
        assert not pawns_can_win(([], queen))
        # without pawns, the latest move was a capture by the queen so white needs to play, so
        # assert queen_can_win(([], queen)) is not valid


def generate_and_evaluate_all_positions_with_one_pawn():
    for pawn in PAWN_SQUARES:
        for queen in SQUARES:
            p = ([pawn], queen)
            if is_valid_pawns_to_play(p):
                pawns_can_win(p)
            if is_valid_queen_to_play(p):
                queen_can_win(p)


def generate_and_evaluate_all_positions_with_two_pawns():
    for pawn1 in PAWN_SQUARES:
        for pawn2 in PAWN_SQUARES:
            if SQUARE_TO_FILE[pawn1] < SQUARE_TO_FILE[pawn2]:
                for queen in SQUARES:
                    p = ([pawn1, pawn2], queen)
                    if is_valid_pawns_to_play(p):
                        pawns_can_win(p)
                    if is_valid_queen_to_play(p):
                        queen_can_win(p)


def generate_and_evaluate_all_positions_with_three_pawns():
    for pawn1 in PAWN_SQUARES:
        for pawn2 in PAWN_SQUARES:
            if SQUARE_TO_FILE[pawn1] < SQUARE_TO_FILE[pawn2]:
                for pawn3 in PAWN_SQUARES:
                    if SQUARE_TO_FILE[pawn2] < SQUARE_TO_FILE[pawn3]:
                        for queen in SQUARES:
                            p = ([pawn1, pawn2, pawn3], queen)
                            if is_valid_pawns_to_play(p):
                                pawns_can_win(p)
                            if is_valid_queen_to_play(p):
                                queen_can_win(p)


def generate_and_evaluate():
    generate_and_evaluate_all_positions_without_pawns()
    evaluation_store.print_stats()
    evaluation_store.print_counts()
    assert len(evaluation_store.store["WHITE"][0]) == 64, len(evaluation_store.store["WHITE"][0])
    generate_and_evaluate_all_positions_with_one_pawn()
    evaluation_store.print_stats()
    evaluation_store.print_counts()
    # white to play:
    #  6 + 6 rook pawns each with 62 queen positions
    #  6 * 6 other pawns each with 61 queen positions
    # so 2 * 6 * 62 + 6 * 6 * 61
    print(len(evaluation_store.store["WHITE"][1]))
    print(2 * 6 * 62 + 6 * 6 * 61)
    assert len(evaluation_store.store["WHITE"][1]) == 2 * 6 * 62 + 6 * 6 * 61
    # black to play:
    #  8 * 7 pawn positions and 63 queen position
    # no pawns: 64
    print(len(evaluation_store.store["BLACK"][1]))
    print(8 * 7 * 63)
    assert len(evaluation_store.store["BLACK"][1]) == 8 * 7 * 63
    evaluation_store.print_stats()
    generate_and_evaluate_all_positions_with_two_pawns()
    evaluation_store.print_stats()
    # generate_and_evaluate_all_positions_with_three_pawns()
    # evaluation_store.print_stats()


def unit_test():
    p = create_position("Qd5")
    assert not pawns_can_win(p)

    p = create_position("b8Qb3")
    assert not queen_can_win(p)

    p = create_position("b7Qd8")
    assert queen_can_win(p)

    p = create_position("b7Qb8")
    assert not pawns_can_win(p)  # Draw

    p = create_position("b6Qb8")
    assert queen_can_win(p)


def main():
    position = initial_position()

    while True:
        if pawns_have_lost(position[0]):
            return
        val, new_pawn = get_eval_pawns_to_play(position, 3)
        position = get_position_after_pawn_play(position, new_pawn)
        print_board(val, get_str_board(position))
        input()

        if pawns_have_won(position[0]):
            return
        val, new_queen = get_eval_queen_to_play(position, 5)
        position = get_position_after_queen_play(position, new_queen)
        print_board(val, get_str_board(position))
        input()


start = timer()
evaluation_store = EvaluationStore()
unit_test()
generate_and_evaluate()
end = timer()
print(end - start)
# main()
evaluation_store.print_counts()
