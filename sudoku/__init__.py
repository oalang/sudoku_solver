from __future__ import annotations
from typing import List
from itertools import product

_PUZZLE_SIZE = 9
_BOX_SIZE = 3
_NUM_SQUARES = _PUZZLE_SIZE ** 2


class Node:
    def __init__(self) -> None:
        self.up = self
        self.down = self
        self.left = self
        self.right = self

    def add_to_row(self, head: Node) -> None:
        self.left = head.left
        self.right = head
        head.left.right = self
        head.left = self

    def add_to_column(self, head: Node) -> None:
        self.up = head.up
        self.down = head
        head.up.down = self
        head.up = self

    def remove_from_row(self) -> None:
        self.right.left = self.left
        self.left.right = self.right

    def remove_from_column(self) -> None:
        self.down.up = self.up
        self.up.down = self.down

    def return_to_row(self) -> None:
        self.right.left = self
        self.left.right = self

    def return_to_column(self) -> None:
        self.down.up = self
        self.up.down = self


class ConstraintNode(Node):
    def __init__(self, index: int) -> None:
        super().__init__()
        self.index = index
        self.possible_count = 0

    def cover(self) -> None:
        self.remove_from_row()

        possibility_node = self
        while (possibility_node := possibility_node.down) != self:
            satisfies_node = possibility_node
            while (satisfies_node := satisfies_node.right) != possibility_node:
                satisfies_node.remove_from_column()
                satisfies_node.constraint.possible_count -= 1

    def uncover(self) -> None:
        possibility_node = self
        while (possibility_node := possibility_node.up) != self:
            satisfies_node = possibility_node
            while (satisfies_node := satisfies_node.left) != possibility_node:
                satisfies_node.return_to_column()
                satisfies_node.constraint.possible_count += 1

        self.return_to_row()


class SatisfiesNode(Node):
    def __init__(self, constraint: ConstraintNode, row: int, col: int, num: int) -> None:
        super().__init__()
        self.constraint = constraint
        self.row = row
        self.col = col
        self.num = num


class Puzzle:
    def __init__(self, clues: List[List[int]]) -> None:
        self.clues = clues
        self.solution = [row[:] for row in clues]
        self.puzzle_matrix = Node()
        self.valid = False
        self.solved = False

        self._build_full_matrix()
        self._apply_clues_to_matrix()

    def _build_full_matrix(self) -> None:
        head = self.puzzle_matrix

        # Generate constraint column headers
        for i in range(_NUM_SQUARES * 4):
            constraint_node = ConstraintNode(i)

            # Insert constraint node into header row
            constraint_node.add_to_row(head)

        # Iterate through every possibility and add a node for each constraint it satisfies
        for row, col, num in product(range(_PUZZLE_SIZE), repeat=3):
            box = (row // _BOX_SIZE) * _BOX_SIZE + (col // _BOX_SIZE)

            # Compute an index for each of four constraint types
            row_col_index = 0 * _NUM_SQUARES + _PUZZLE_SIZE * row + col
            row_num_index = 1 * _NUM_SQUARES + _PUZZLE_SIZE * row + num
            col_num_index = 2 * _NUM_SQUARES + _PUZZLE_SIZE * col + num
            box_num_index = 3 * _NUM_SQUARES + _PUZZLE_SIZE * box + num

            satisfies = {row_col_index, row_num_index, col_num_index, box_num_index}

            constraint_node = head
            first_satisfies_node = None

            # Iterate through each constraint and check if it is satisfied
            while (constraint_node := constraint_node.right) != head:
                if constraint_node.index in satisfies:
                    satisfies_node = SatisfiesNode(constraint_node, row, col, num + 1)

                    # Insert satisfies node into constraint column
                    satisfies_node.add_to_column(constraint_node)
                    constraint_node.possible_count += 1

                    if first_satisfies_node is None:
                        first_satisfies_node = satisfies_node
                    else:
                        # Insert satisfies node into possibility row
                        satisfies_node.add_to_row(first_satisfies_node)

    def _apply_clues_to_matrix(self) -> None:
        head = self.puzzle_matrix
        self.valid = True

        for row, col in product(range(_PUZZLE_SIZE), repeat=2):
            num = self.solution[row][col]

            if num:
                constraint_node = head
                found = 0

                while not found and (constraint_node := constraint_node.right) != head:
                    possibility_node = constraint_node
                    while not found and (possibility_node := possibility_node.down) != constraint_node:
                        if possibility_node.row == row and possibility_node.col == col and possibility_node.num == num:
                            satisfies_node = possibility_node
                            while True:
                                found += 1
                                satisfies_node.constraint.cover()
                                if (satisfies_node := satisfies_node.right) == possibility_node:
                                    break
                if found != 4:
                    self.valid = False
                    break

    def solve(self) -> None:
        if self._find_solution() and self._valid_solution():
            self.solved = True

    def _find_solution(self) -> bool:
        solution = self.solution
        head = self.puzzle_matrix

        if head.right == head:
            return True

        constraint_node = self._choose_constraint()
        constraint_node.cover()

        possibility_node = constraint_node
        while (possibility_node := possibility_node.down) != constraint_node:
            satisfies_node = possibility_node
            while (satisfies_node := satisfies_node.right) != possibility_node:
                satisfies_node.constraint.cover()

            if self._find_solution():
                solution[possibility_node.row][possibility_node.col] = possibility_node.num
                return True

            satisfies_node = possibility_node
            while (satisfies_node := satisfies_node.left) != possibility_node:
                satisfies_node.constraint.uncover()

        constraint_node.uncover()
        return False

    def _choose_constraint(self) -> ConstraintNode:
        head = self.puzzle_matrix
        choice = None
        min_count = _PUZZLE_SIZE + 1

        constraint_node = head
        while (constraint_node := constraint_node.right) != head:
            if constraint_node.possible_count < min_count:
                choice = constraint_node
                min_count = constraint_node.possible_count

        return choice

    def _valid_solution(self) -> bool:
        clues = self.clues
        solution = self.solution
        constraints = [False] * (4 * _NUM_SQUARES)

        for row, col in product(range(_PUZZLE_SIZE), repeat=2):
            # Check that the original clue is included in the solution
            if clues[row][col] and solution[row][col] != clues[row][col]:
                return False

            # Check that the solution has a valid entry in every box
            if solution[row][col] < 1 or solution[row][col] > _PUZZLE_SIZE:
                return False

            box = (row // _BOX_SIZE) * _BOX_SIZE + (col // _BOX_SIZE)
            num = solution[row][col] - 1

            # Compute an index for each of four constraint types
            row_col_index = 0 * _NUM_SQUARES + _PUZZLE_SIZE * row + col
            row_num_index = 1 * _NUM_SQUARES + _PUZZLE_SIZE * row + num
            col_num_index = 2 * _NUM_SQUARES + _PUZZLE_SIZE * col + num
            box_num_index = 3 * _NUM_SQUARES + _PUZZLE_SIZE * box + num

            if (constraints[row_col_index] or constraints[row_num_index] or
                    constraints[col_num_index] or constraints[box_num_index]):
                return False

            constraints[row_col_index] = True
            constraints[row_num_index] = True
            constraints[col_num_index] = True
            constraints[box_num_index] = True

        for constraint in constraints:
            if not constraint:
                return False

        return True

    def is_valid(self) -> bool:
        return self.valid

    def is_solved(self) -> bool:
        return self.solved

    def display(self) -> None:
        for row in self.solution:
            for num in row:
                print(f"{num} " if num else ". ", end='')
            print()
