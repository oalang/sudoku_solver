"""
A Sudoku solver using Knuth's Algorithm X implemented with dancing links (DLX).

https://github.com/oalang/sudoku_solver

Implements the algorithm described in:
    | https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X

A Puzzle object is built from a 9x9 array of clues (nested lists). Empty boxes are represented by '0'.
The constructor checks if the clues produce a valid puzzle. The solver checks if the solution is valid.

Example:
    >>> from sudoku import Puzzle
    >>> clues = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
    ...          [6, 0, 0, 1, 9, 5, 0, 0, 0],
    ...          [0, 9, 8, 0, 0, 0, 0, 6, 0],
    ...          [8, 0, 0, 0, 6, 0, 0, 0, 3],
    ...          [4, 0, 0, 8, 0, 3, 0, 0, 1],
    ...          [7, 0, 0, 0, 2, 0, 0, 0, 6],
    ...          [0, 6, 0, 0, 0, 0, 2, 8, 0],
    ...          [0, 0, 0, 4, 1, 9, 0, 0, 5],
    ...          [0, 0, 0, 0, 8, 0, 0, 7, 9]]
    >>> puzzle = Puzzle.(clues) # Build puzzle
    >>> puzzle.display()        # Display puzzle
    >>> puzzle.is_valid()       # Check puzzle validity
    >>> puzzle.solve()          # Solve the puzzle
    >>> puzzle.is_solved()      # Check solution validity
    >>> puzzle.display()        # Display solution
"""

from __future__ import annotations
from typing import List
from itertools import product

_PUZZLE_SIZE = 9
_BOX_SIZE = 3
_NUM_SQUARES = _PUZZLE_SIZE ** 2


class Node:
    """Represents a node in the dancing links data structure.

    Attributes:
        up (Node): The next node up
        down (Node): The next node down
        left (Node): The next node left
        right (Node): The next node right
    """

    def __init__(self) -> None:
        """Initialize a node pointing to itself in every direction."""

        self.up = self
        self.down = self
        self.left = self
        self.right = self

    def add_to_row(self, head: Node) -> None:
        """Add the node to a row, left of the head node."""

        self.left = head.left
        self.right = head
        head.left.right = self
        head.left = self

    def add_to_column(self, head: Node) -> None:
        """Add the node to a column, above the head node."""

        self.up = head.up
        self.down = head
        head.up.down = self
        head.up = self

    def remove_from_row(self) -> None:
        """Remove the node from its row."""

        self.right.left = self.left
        self.left.right = self.right

    def remove_from_column(self) -> None:
        """Remove the node from its column."""

        self.down.up = self.up
        self.up.down = self.down

    def return_to_row(self) -> None:
        """Return the node to its former position in the row."""

        self.right.left = self
        self.left.right = self

    def return_to_column(self) -> None:
        """Return the node to its former position in the column."""

        self.down.up = self
        self.up.down = self


class ConstraintNode(Node):
    """Represents a constraint that must be satisfied.

    Attributes:
        index (int): A unique index which identifies the constraint.
        possibility_count (int): The number of remaining possibilities that satisfy the constraint.
    """

    def __init__(self, index: int) -> None:
        """Initialize a constraint node with and index and a zero possibility count.

        Args:
            index: A unique index which identifies the constraint.
        """

        super().__init__()
        self.index = index
        self.possibility_count = 0

    def cover(self) -> None:
        """Cover the constraint.

        Removes its node from the constraint row. Then removes each possibility in its column from
        every other column where it appears.
        """
        self.remove_from_row()

        possibility_node = self
        while (possibility_node := possibility_node.down) != self:
            satisfies_node = possibility_node
            while (satisfies_node := satisfies_node.right) != possibility_node:
                satisfies_node.remove_from_column()
                satisfies_node.constraint.possibility_count -= 1

    def uncover(self) -> None:
        """Uncover the constraint.

        Undoes the cover operation by performing the opposite of each of its steps, in reverse order.
        """

        possibility_node = self
        while (possibility_node := possibility_node.up) != self:
            satisfies_node = possibility_node
            while (satisfies_node := satisfies_node.left) != possibility_node:
                satisfies_node.return_to_column()
                satisfies_node.constraint.possibility_count += 1

        self.return_to_row()


class SatisfiesNode(Node):
    """Represents the relationship between a possibility and a constraint it satisfies.

    Attributes:
        constraint (ConstraintNode): The node representing the constraint being satisfied.
        row (int): The row index of square being filled.
        col (int): The column index of the square being filled.
        num (int): The number filling the square.
    """

    def __init__(self, constraint: ConstraintNode, row: int, col: int, num: int) -> None:
        """Initialize a satisfies node.

        Args:
            constraint: The node representing the constraint being satisfied.
            row: The row index of square being filled.
            col: The column index of the square being filled.
            num: The number filling the square.
        """

        super().__init__()
        self.constraint = constraint
        self.row = row
        self.col = col
        self.num = num


class Puzzle:
    def __init__(self, clues: List[List[int]]) -> None:
        self.clues = clues
        self.solution = [row[:] for row in clues]
        self.head_node = Node()
        self.valid_puzzle = False
        self.valid_solution = False

        self._build_full_matrix()
        self._apply_clues_to_matrix()

    def _build_full_matrix(self) -> None:
        head_node = self.head_node

        # Generate constraint column headers.
        for i in range(_NUM_SQUARES * 4):
            constraint_node = ConstraintNode(i)

            # Insert constraint node into header row.
            constraint_node.add_to_row(head_node)

        # Iterate through every possibility and add a node for each constraint it satisfies.
        for row, col, num in product(range(_PUZZLE_SIZE), repeat=3):
            box = (row // _BOX_SIZE) * _BOX_SIZE + (col // _BOX_SIZE)

            # Compute an index for each of four constraint types.
            row_col_index = 0 * _NUM_SQUARES + _PUZZLE_SIZE * row + col
            row_num_index = 1 * _NUM_SQUARES + _PUZZLE_SIZE * row + num
            col_num_index = 2 * _NUM_SQUARES + _PUZZLE_SIZE * col + num
            box_num_index = 3 * _NUM_SQUARES + _PUZZLE_SIZE * box + num

            satisfies = {row_col_index, row_num_index, col_num_index, box_num_index}

            constraint_node = head_node
            first_satisfies_node = None

            # Iterate through each constraint and check if it is satisfied.
            while (constraint_node := constraint_node.right) != head_node:
                if constraint_node.index in satisfies:
                    satisfies_node = SatisfiesNode(constraint_node, row, col, num + 1)

                    # Insert satisfies node into constraint column.
                    satisfies_node.add_to_column(constraint_node)
                    constraint_node.possibility_count += 1

                    if first_satisfies_node is None:
                        first_satisfies_node = satisfies_node
                    else:
                        # Insert satisfies node into possibility row.
                        satisfies_node.add_to_row(first_satisfies_node)

    def _apply_clues_to_matrix(self) -> None:
        head_node = self.head_node

        for row, col in product(range(_PUZZLE_SIZE), repeat=2):
            num = self.solution[row][col]
            if num:
                constraint_node = head_node
                found = 0

                while not found and (constraint_node := constraint_node.right) != head_node:
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
                    self.valid_puzzle = False
                    break

        self.valid_puzzle = True

    def solve(self) -> None:
        if self._find_solution() and self._validate_solution():
            self.valid_solution = True

    def _find_solution(self) -> bool:
        solution = self.solution
        head_node = self.head_node

        if head_node.right == head_node:
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
        head_node = self.head_node
        choice = None
        min_count = _PUZZLE_SIZE + 1

        constraint_node = head_node
        while (constraint_node := constraint_node.right) != head_node:
            if constraint_node.possibility_count < min_count:
                choice = constraint_node
                min_count = constraint_node.possibility_count

        return choice

    def _validate_solution(self) -> bool:
        clues = self.clues
        solution = self.solution
        constraints = [False] * (4 * _NUM_SQUARES)

        for row, col in product(range(_PUZZLE_SIZE), repeat=2):
            # Check that the original clue is included in the solution.
            if clues[row][col] and solution[row][col] != clues[row][col]:
                return False

            # Check that the solution has a valid entry in every box.
            if solution[row][col] < 1 or solution[row][col] > _PUZZLE_SIZE:
                return False

            box = (row // _BOX_SIZE) * _BOX_SIZE + (col // _BOX_SIZE)
            num = solution[row][col] - 1

            # Compute an index for each of four constraint types.
            row_col_index = 0 * _NUM_SQUARES + _PUZZLE_SIZE * row + col
            row_num_index = 1 * _NUM_SQUARES + _PUZZLE_SIZE * row + num
            col_num_index = 2 * _NUM_SQUARES + _PUZZLE_SIZE * col + num
            box_num_index = 3 * _NUM_SQUARES + _PUZZLE_SIZE * box + num

            # Check that each constraint is satisfied no more than once.
            if (constraints[row_col_index] or constraints[row_num_index] or
                    constraints[col_num_index] or constraints[box_num_index]):
                return False

            constraints[row_col_index] = True
            constraints[row_num_index] = True
            constraints[col_num_index] = True
            constraints[box_num_index] = True

        # Check that each constraint has been satisfied.
        for constraint in constraints:
            if not constraint:
                return False

        return True

    def is_valid(self) -> bool:
        return self.valid_puzzle

    def is_solved(self) -> bool:
        return self.valid_solution

    def display(self) -> None:
        for row in self.solution:
            for num in row:
                print(f"{num} " if num else ". ", end='')
            print()
