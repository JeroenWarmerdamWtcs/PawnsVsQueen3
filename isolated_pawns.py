from itertools import combinations
from basics import *
from evaluation import pawns_can_win
from generator import generate_all_positions_with_isolated_pawns


def isolated_pawns_only_and_queen_might_just_have_captured_non_isolated_pawn(p: Position) -> bool:
    pawn_files = set(SQUARE_TO_FILE[pawn] for pawn in p.pawns)
    queen_file = SQUARE_TO_FILE[p.queen]
    return all((p.is_valid_pawns_to_play(),
                p.queen in PAWN_SQUARES,
                len(pawn_files) == 1 or min(abs(f1 - f2) for f1, f2 in combinations(pawn_files, 2)) > 1,
                min(abs(queen_file - pawn_file) for pawn_file in pawn_files) == 1))


def isolated_pawns_can_win(p: Position) -> bool:
    assert isolated_pawns_only_and_queen_might_just_have_captured_non_isolated_pawn(p)
    front_rank = max(SQUARE_TO_RANK[pawn] for pawn in p.pawns)
    queen_file, queen_rank = SQUARES_TO_FILE_AND_RANK[p.queen]
    if front_rank == 7:
        return True  # immediate promotion, as the queen is in another file
    if queen_rank == 7:
        return False  # queen wil stay on 7th rank, capturing any pawn going to 7th rank
    if front_rank <= 5:
        return False  # queen can move vertically to 8th rank.
        # If a pawn arrives at rank 7, block and win. Then all other pawn are below 7th rank.
        # If there is no pawn on rank 7, go to 6th rank and adjacent file containing a pawn.

    # So now: front_rank == 6 and queen_rank < 7
    # ==========================================
    pawns_in_front = [pawn for pawn in p.pawns if SQUARE_TO_RANK[pawn] == 6]
    if len(pawns_in_front) > 2:
        return True
    if len(pawns_in_front) == 2:
        # Usually the pawns can win, but there are exceptions:
        file1, file2 = sorted([SQUARE_TO_FILE[pawn] for pawn in pawns_in_front])
        if queen_rank == 6 and file1 + 1 == queen_file == file2 - 1:
            return False
            # 8:  . . . . .
            # 7:  . . . . .     queen will win, addition pawns on lower ranks do not help
            # 6:  . p Q p .

        if (queen_rank == 4 and file1 + 3 == queen_file == file2 - 3 and
                NEXT_SQUARE[p.queen][Direction.NW] not in p.pawns and
                NEXT_SQUARE[p.queen][Direction.NE] not in p.pawns):
            # 8:  . . . . . . . .
            # 7:  . . . . . . . .    There must be a pawn in a file adjacent to the queen,
            # 6:  p . . . . . p .    but 5th rank will block winning move.
            # 5:  . . . . . . . .
            # 4:  . . p Q . . . .
            return False

        return True
        # (queen_rank == 5 and file1 + 2 == queen_file == file2 - 2 does not have
        #  room for an isolated pawn next to the queen file)

    # So now: one pawn on rank 6, none on higher ranks, queen on rank 6 or lower
    # ==========================================================================

    front_pawn = next(pawn for pawn in p.pawns if SQUARE_TO_RANK[pawn] == 6)
    front_pawn_file = SQUARE_TO_FILE[front_pawn]
    file_diff = abs(front_pawn_file - queen_file)
    direction = Direction.NW if front_pawn_file < queen_file else Direction.NE
    file_step = -1 if front_pawn_file < queen_file else 1
    queen_destination_rank_in_front_pawn_file = queen_rank + file_diff
    if queen_destination_rank_in_front_pawn_file not in (7, 8):
        return True  # white can advance the front pawn, and cannot be blocked or captured

    sq = p.queen
    while True:
        sq = NEXT_SQUARE[sq][direction]
        if sq in p.pawns:
            return True  # white can advance the front pawn, the pawn on sq intercepts the queen
        if SQUARE_TO_RANK[sq] >= 6:  # No more pawns on higher rank
            break

    if queen_destination_rank_in_front_pawn_file == 7:
        return False
        # whether White will advance the front pawn or not, the queen will go to it's file and 7th rank.

    # So now: one pawn on rank 6 and one or more on lower ranks,
    # queen has rank 6 or lower and attacks the promotion square of the front pawn
    # ============================================================================

    # If white plays the front pawn, the queen will first block and then capture it, winning the game.
    # So white need to advance another pawn. This must be a pawn in a file adjacent to the file of the queen going
    # to rank 6 preventing the queen from going to rank 7 vertically.

    adjacent_file = queen_file - file_step  # first we try the file on the opposite side of the front pawn
    if adjacent_file in FILES and FILE_RANK_TO_SQUARE[adjacent_file][5] in p.pawns:
        # so there is a pawn on rank 5 in the file adjacent to the file of the queen
        # on the opposite side of the front pawn
        # queen can win <==> rank of queen is 5 or higher with two exceptions on rank 4:
        if queen_rank == 6:
            assert False  # cannot happen as pawn attacks queen
        if queen_rank == 5:
            return False
            # If queen is on rank 5, she moves horizontally one step in the direction of the file of the front pawn.
            # Now she attacks both squares (*) on 7th rank in front of the two 6th rank pawns.
            # If one advances, the queen captures it. Otherwise, she goes to one of these squares.
            #   8: . . . . . . .          8: . . . . . . .
            #   7: . . . . . . .   ---\   7: . * . . . * .
            #   6: . p . . . . .   ---/   6: . p . . . p .
            #   5: . . . . Q p .          5: . . . Q . . .
            # No additional isolated pawn could help.
        if p.queen in str_to_squares("d4e4"):
            return False
            #   #  a b c d e f g h
            #   8: . . . . . . . .      f6? Qh7!
            #   7: . . . . . . . .
            #   6: p . . . . . . .
            #   5: . . . . . p . .
            #   4: . . . . Q . . .
        return True
        #   Queen cannot go to rank 7:
        #   - not diagonally in one direction, because the front pawn attacks that square
        #   - not diagonally in the other direction. The only exception are given above
        #   - not vertically, because 5th rank pawn advances attacks that square
        #   Queen cannot go behind on pawn attacking the 7th rank square in front of the other pawn
        #   Queen cannot go to square in the middle attacking both 7th rank squares

    adjacent_file = queen_file + file_step  # now we try the file on the same side of the front pawn
    if FILE_RANK_TO_SQUARE[adjacent_file][5] in p.pawns:
        # so there is a pawn on rank 5 in the file adjacent to the file of the queen
        # on the side of the front pawn

        # Queen might go horizontally towards the file of one of the pawn. Then, neither pawn can advance.
        # A third pawn might intercept both diagonal moves.
        # (There is no room for two isolated pawns to intercept one diagonal move each.)
        if queen_rank == 3 and FILE_RANK_TO_SQUARE[queen_file + 3 * file_step][5] in p.pawns:
            return True
            #   8: . . . . . . . .
            #   7: . . . . . . . .  e6 wins: Qc3? e7! Qe3? a7! (pawn in c5 intercepts)
            #   6: p . . . . . . .
            #   5: . . p . p . . .
            #   4: . . . . . . . .
            #   3: . . . . . Q . .
        return False
        #   8: . . . . . . . .
        #   7: . . . . . . . .  e6? Qa4 or Qe4!
        #   6: p . . . . . . .
        #   5: . . . p . . . .
        #   4: . . . . Q . . .
        #   3: . . . . . . . .

    # So now: one pawn on rank 6 and one or more on lower ranks,
    # but no pawn on rank 5 in the file adjacent to the file of the queen.
    # Queen attacks the promotion square of the front pawn on rank 6 or lower
    # ==================================================================================

    return False
    #   Queen either blocks the front pawn if that advances,
    #   or goes vertically to rank 7.


def run_test() -> None:
    for p in generate_all_positions_with_isolated_pawns():
        if isolated_pawns_only_and_queen_might_just_have_captured_non_isolated_pawn(p):
            assert isolated_pawns_can_win(p) == pawns_can_win(p)


if __name__ == "__main__":
    run_test()
    print("All tests passed")
