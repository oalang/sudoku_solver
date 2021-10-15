# sodoku_solver

A Sudoku solver using Knuth's Algorithm X implemented with dancing links (DLX).

https://github.com/oalang/sudoku_solver

Implements the algorithm described in:

https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X

## USAGE INSTRUCTIONS

A Puzzle object is built from an array of clues (a nested list of lists). Empty squares are represented by '0'.
The constructor checks if the clues produce a valid puzzle. The solver checks if the solution is valid.

### Python Console Example:

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

### Sample Script:

    ./example/solve_puzzle.py
