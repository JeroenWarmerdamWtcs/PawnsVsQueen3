from evaluation_repository import *


def update_if_queen_can_capture_pawn_on_rank7(pawns, move, queen_board_value):
    # Updates queen_board_value for squares sq in case:
    #   - the pawn after moving to rank 7 is not defended and can be captured by the queen on square sq
    # The values do not include the pawn move and queen move
    o, d = move  # so SQUARE_TO_RANK[d] == 7
    if pawns.attack[d]:
        # queen_board_value_black_to_play[d] was initialized to PAWNS_WIN_IN_ONE, so
        # capturing the pawn will improve the value
        return
    pawns.remove(o)
    position_after_queen_captures_pawn = Position(pawns, queen=d)
    result_if_queen_captures_pawn = repo_pawns_can_win[position_after_queen_captures_pawn]
    for queen_square in position_after_queen_captures_pawn.get_queen_origins():
        # Note that queen_square might be o or an attached square. But those returned values will not be used.
        queen_board_value[queen_square] = result_if_queen_captures_pawn
    pawns.add(o)


def update_if_queen_can_blocks_pawn_on_rank_7(pawns, move, queen_board_value):
    # update queen_board_value, for squares
    # from where the queen can block the pawn on rank 7
    o, d = move  # so SQUARE_TO_RANK[d] == 7
    o_was_defended = pawns.attack[o] > 0
    pawns.move(o, d)

    # determine result_if_queen_blocks
    if len(pawns.squares) == 1:
        result_if_queen_blocks = DRAW
        # only pawn left cannot move
    elif o_was_defended:
        result_if_queen_blocks = PAWNS_WIN_IN_2
        # Move 1: Advance the pawn that defends o (possible as queen blocks other pawn).
        # It will now defend the pawn on d again.
        # The queen cannot capture the pawn on d and must leave its square.
        # Move 2: The pawn on d will promote
    elif any(pawn for pawn in pawns.squares if SQUARE_TO_RANK[pawn] == 6):
        result_if_queen_blocks = PAWNS_WIN_IN_2
        # Move 1: Advance a second pawn to rank 7.
        # The queen cannot capture both pawns or block both pawns.
        # Move 2: Promote a pawn that is not blocked nor captured.
    else:
        #  White has lower pawns, none on rank 6 and none can move to rank 6 to defend the pawn on rank 7.
        #  So white does the best pawn move and black will capture the pawn on rank 7 next.
        #  As we know the queen move, we can improve performance by first doing the queen move and next
        #  try pawn move and evaluate if pawns still need to play.
        pawns.remove(d)
        position_after_queen_captures = Position(pawns, d)  # queen on rank 7 after it captured the pawn
        result_if_queen_captures_pawn = QUEEN_HAS_WON  # this value will be overwritten as there are pawns left
        list_of_pawn_moves = position_after_queen_captures.get_pawn_moves()
        for o2, d2 in list_of_pawn_moves:
            position_after_queen_captures.play_pawn(o2, d2)
            value = repo_pawns_can_win[position_after_queen_captures]
            if value > result_if_queen_captures_pawn:
                result_if_queen_captures_pawn = value
            position_after_queen_captures.play_back_pawn()
        result_if_queen_blocks = add_one_move(result_if_queen_captures_pawn)
        pawns.add(d)

    position_after_queen_blocks = Position(pawns, N[d])
    queen_origins = position_after_queen_blocks.get_queen_origins()
    for queen_square in queen_origins:
        queen_board_value[queen_square] = result_if_queen_blocks

    pawns.move(d, o)
