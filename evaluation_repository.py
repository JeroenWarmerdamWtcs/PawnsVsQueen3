class EvaluationRepository:
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


def print_repo_stats():
    repo_pawns_can_win.print_stats()
    repo_queen_can_win.print_stats()
    repo_pawns_can_win.print_counts()
    repo_queen_can_win.print_counts()


repo_pawns_can_win = EvaluationRepository()
repo_queen_can_win = EvaluationRepository()
