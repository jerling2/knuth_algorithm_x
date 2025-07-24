import os
from linkedList2D import LinkedList2D, Node2D


DATA_PATH = './data'


class ExactCover(LinkedList2D):
    def __init__(self):
        super().__init__()

    def load(self, pathname):
        super().load(pathname)

    def solve(self):
        fringe = [(0, [], node) for node in self.get_nodes_from_column(self.get_min_column())]
        solutions = []
        while fringe:
            num_restores, partial_solution, fringe_node = fringe.pop()
            partial_solution.append(fringe_node)
            columns = self.get_columns_from_row(fringe_node)
            num_restores += len(columns)
            for column in columns:
                self.remove_column(column)
            min_col = self.get_min_column()
            if min_col is self.head:
                solutions.append([self.get_row_from_node(node) for node in partial_solution])
                for _ in range(num_restores):
                    self.restore()
                continue
            if min_col.value < 0:
                raise Exception("bounds error!")
            if min_col.value == 0:
                for _ in range(num_restores):
                    self.restore()
                continue
            for branch_num, node in enumerate(self.get_nodes_from_column(min_col)):
                if branch_num == 0:
                    fringe.append((num_restores, partial_solution, node))
                else:
                    fringe.append((0, partial_solution, node))
        return solutions


def main():
    filename = input("Enter filename of matrix (w/o ext): ")
    pathname = os.path.join(DATA_PATH, filename + '.mtx')
    if not os.path.exists(pathname):
        return print(f"File error: '{pathname}' does not exist.")
    solver = ExactCover()
    try:
        solver.load(pathname)
    except Exception as error:
        return print(f"Encountered an error while trying to load: {error}")
    solutions = solver.solve()
    counter = 1
    for solution in solutions:
        message = "." * 4  + f"Solution {counter}\n"
        counter += 1
        for row in solution:
            message += ", ".join([f"{node.value}" for node in row]) + "\n"
        print(message.rstrip())

if __name__ == "__main__":
    main()