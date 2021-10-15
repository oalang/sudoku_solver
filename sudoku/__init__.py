"""
A Sudoku solver using Knuth's Algorithm X implemented with dancing links (DLX).

https://github.com/oalang/sudoku_solver

Implements the algorithm described in:
https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X

A Puzzle object is built from an array of clues (a nested list of lists). Empty squares are represented by '0'.
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
    >>> puzzle = Puzzle.(clues)  # Build puzzle
    >>> puzzle.display()         # Display puzzle
    >>> puzzle.is_valid()        # Check puzzle validity
    >>> puzzle.solve()           # Solve puzzle
    >>> puzzle.is_solved()       # Check solution validity
    >>> puzzle.display()         # Display solution
"""

from __future__ import annotations
from typing import List, Tuple
from math import isqrt
from itertools import product


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
        """Add the node to a row, left of the head node.

        Args:
            head: The row's head node.
        """

        self.left = head.left
        self.right = head
        head.left.right = self
        head.left = self

    def add_to_column(self, head: Node) -> None:
        """Add the node to a column, above the head node.

        Args:
            head: The column's head node.
        """

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
        """Initialize a constraint node with an index and possibility count zero.

        Args:
            index: A unique index which identifies the constraint.
        """

        super().__init__()
        self.index = index
        self.possibility_count = 0

    def cover(self) -> None:
        """Cover the constraint.

        Removes its node from the constraint row. Then removes each possibility in its column from
        the other columns where it appears.
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
        row (int): The row index of square being filled.
        col (int): The column index of the square being filled.
        num (int): The number filling the square.
        constraint (ConstraintNode): The node representing the constraint being satisfied.
    """

    def __init__(self, row: int, col: int, num: int, constraint: ConstraintNode) -> None:
        """Initialize a satisfies node.

        Args:
            row: The row index of square being filled.
            col: The column index of the square being filled.
            num: The number filling the square.
            constraint: The node representing the constraint being satisfied.
        """

        super().__init__()
        self.row = row
        self.col = col
        self.num = num
        self.constraint = constraint


class Puzzle:
    """Represents a puzzle to be solved.

    Attributes:
        valid_puzzle (bool): Is the puzzle valid.
        valid_solution (bool): Has a valid solution been found.
        box_size (int): The problem's subgrids have dimensions box_size x box_size.
        puzzle_size (int): The problem's grid has dimensions puzzle_size x puzzle_size.
        num_squares (int): The total number of squares.
        num_constraints (int): The number of constraints that must be satisfied.
        clues (List[List[int]]): The puzzle_size x puzzle_size array of clues.
        solution (List[List[int]]): The puzzle_size x puzzle_size solution array.
        head_node (Node): The head node of the dancing links data structure.
        constraint_nodes (List[ConstraintNode]): A list enumerating the constraint nodes.
    """

    def __init__(self, clues: List[List[int]]) -> None:
        """Initialize a puzzle from a clues array.

        Checks the validity of the clues array's dimensions, then builds the dancing links matrix
        and prunes it by applying the given clues.

        Args:
            clues: An array of nested lists representing the given clues.
        """

        self.valid_puzzle = False
        self.valid_solution = False

        self.box_size = isqrt(len(clues))
        self.puzzle_size = self.box_size ** 2
        self.num_squares = self.puzzle_size ** 2
        self.num_constraints = self.num_squares * 4

        if self.box_size ** 2 != self.puzzle_size:
            return
        for row in clues:
            if len(row) != self.puzzle_size:
                return

        self.clues = clues
        self.solution = [row[:] for row in clues]
        self.head_node = Node()
        self.constraint_nodes = [ConstraintNode(i) for i in range(self.num_constraints)]

        self._build_full_matrix()
        self._apply_clues_to_matrix()

    def _build_full_matrix(self) -> None:
        """Build the dancing links matrix."""

        # Add constraint nodes to the header row.
        for constraint_node in self.constraint_nodes:
            constraint_node.add_to_row(self.head_node)

        # Iterate through every possibility and add a node for each constraint it satisfies.
        for row, col, num in product(range(self.puzzle_size), repeat=3):
            first_satisfies_node = None

            for constraint_node in [self.constraint_nodes[i] for i in self._satisfied_by(row, col, num)]:
                satisfies_node = SatisfiesNode(row, col, num + 1, constraint_node)

                satisfies_node.add_to_column(constraint_node)
                constraint_node.possibility_count += 1

                if first_satisfies_node is None:
                    first_satisfies_node = satisfies_node
                else:
                    satisfies_node.add_to_row(first_satisfies_node)

    def _apply_clues_to_matrix(self) -> None:
        """Prune the dancing links matrix by applying the given clues and check the validity of the puzzle."""

        constraint_satisfied = [False] * self.num_constraints

        # For each non-zero entry in the clues array, cover every constraint that is satisfied by the clue.
        for row, col in product(range(self.puzzle_size), repeat=2):
            clues_num = self.clues[row][col]
            if clues_num:
                for i in self._satisfied_by(row, col, clues_num - 1):
                    # Check that each constraint is satisfied no more than once.
                    if constraint_satisfied[i]:
                        self.valid_puzzle = False
                        return
                    constraint_satisfied[i] = True
                    self.constraint_nodes[i].cover()

        self.valid_puzzle = True

    def solve(self) -> None:
        """If the puzzle is valid, search for a solution and validate it."""

        if not self.is_valid():
            print("This puzzle is not valid.")
            return
        if self._find_solution() and self._validate_solution():
            self.valid_solution = True

    def _find_solution(self) -> bool:
        """Recursively search for a solution for the current state of the problem matrix.

        Returns:
            True if a solution has been found and False otherwise.
        """

        # If the problem matrix is empty, all constraints have been satisfied (i.e., a solution has been found).
        # In which case, return True.
        if self.head_node.right == self.head_node:
            return True

        # Otherwise, deterministically choose a constraint to satisfy and cover it.
        constraint_node = self._choose_constraint()
        constraint_node.cover()

        # Iterate through each possibility which satisfies the chosen constraint and check if it results in a successful
        # search path.
        possibility_node = constraint_node
        while (possibility_node := possibility_node.down) != constraint_node:
            # Cover all remaining constraints satisfied by the possibility.
            satisfies_node = possibility_node
            while (satisfies_node := satisfies_node.right) != possibility_node:
                satisfies_node.constraint.cover()

            # Check if a solution exists down this search path. If one does exist, enter the possibility into the
            # solution array and return True.
            if self._find_solution():
                self.solution[possibility_node.row][possibility_node.col] = possibility_node.num
                return True

            # The possibility does not result in a successful search path, so uncover the constraints which have been
            # covered, in reverse order, and try the next possibility, if one exists.
            satisfies_node = possibility_node
            while (satisfies_node := satisfies_node.left) != possibility_node:
                satisfies_node.constraint.uncover()

        # None of the possibilities which satisfy the chosen constraint produce a successful search path, so uncover the
        # chosen constraint and return False to backtrack.
        constraint_node.uncover()
        return False

    def _choose_constraint(self) -> ConstraintNode:
        """Deterministically choose a constraint.

        Returns:
            The leftmost remaining constraint node with the minimum number of remaining possibilities.
        """

        choice = None
        min_count = self.puzzle_size + 1

        constraint_node = self.head_node
        while (constraint_node := constraint_node.right) != self.head_node:
            if constraint_node.possibility_count < min_count:
                choice = constraint_node
                min_count = constraint_node.possibility_count

        return choice

    def _validate_solution(self) -> bool:
        """Validate the solution.

        Returns:
            True if valid and False otherwise.
        """

        constraint_satisfied = [False] * self.num_constraints

        for row, col in product(range(self.puzzle_size), repeat=2):
            clues_num = self.clues[row][col]
            solution_num = self.solution[row][col]

            # Check that the original clue is included in the solution.
            if clues_num and solution_num != clues_num:
                return False

            # Check that the solution has a valid entry in every square.
            if solution_num < 1 or solution_num > self.puzzle_size:
                return False

            for i in self._satisfied_by(row, col, solution_num - 1):
                # Check that each constraint is satisfied no more than once.
                if constraint_satisfied[i]:
                    return False
                constraint_satisfied[i] = True

        # Check that each constraint has been satisfied.
        for satisfied in constraint_satisfied:
            if not satisfied:
                return False

        return True

    def _satisfied_by(self, row: int, col: int, num: int) -> Tuple[int, int, int, int]:
        """Compute the indices of the constrains satisfied by a possibility.

        Args:
            row: The row index of square being filled.
            col: The column index of the square being filled.
            num: The number filling the square.

        Returns:
            A tuple of four indices.
        """

        box = (row // self.box_size) * self.box_size + (col // self.box_size)

        row_col_index = 0 * self.num_squares + self.puzzle_size * row + col  # row-column constraint
        row_num_index = 1 * self.num_squares + self.puzzle_size * row + num  # row-number constraint
        col_num_index = 2 * self.num_squares + self.puzzle_size * col + num  # column-number constraint
        box_num_index = 3 * self.num_squares + self.puzzle_size * box + num  # box-number constraint

        return row_col_index, row_num_index, col_num_index, box_num_index

    def is_valid(self) -> bool:
        """Get the valid_puzzle attribute.

        Returns:
            The boolean valid_puzzle attribute.
        """

        return self.valid_puzzle

    def is_solved(self) -> bool:
        """Get the valid_solution attribute.

        Returns:
            The boolean valid_solution attribute.
        """

        return self.valid_solution

    def display(self) -> None:
        """Display the current state of the solution array."""

        for row in self.solution:
            for num in row:
                print(f"{num} " if num else ". ", end='')
            print()
