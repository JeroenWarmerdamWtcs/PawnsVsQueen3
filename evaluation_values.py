UNKNOWN = 0
QUEEN_HAS_WON = 1
QUEEN_WINS_IN_1 = 2
QUEEN_WINS_IN_2 = 3
QUEEN_WINS_IN_3 = 4
DRAW = 128
PAWNS_HAVE_WON = 255
PAWNS_WIN_IN_1 = 254
PAWNS_WIN_IN_2 = 253
PAWNS_WIN_IN_3 = 252


def value_to_str(outcome):
    if outcome == UNKNOWN:
        return " ? "
    if outcome == DRAW:
        return " = "
    if outcome < DRAW:
        # queen has won
        if outcome == QUEEN_HAS_WON:
            return "-0"
        else:
            return str(QUEEN_HAS_WON - outcome)
    else:
        return '+' + str(PAWNS_HAVE_WON - outcome)


def add_one_move(value):
    if value > DRAW:
        return value - 1
    if value < DRAW:
        return value + 1
    return value


def add_two_moves(value):
    if value > DRAW:
        return value - 2
    if value < DRAW:
        return value + 2
    return value
