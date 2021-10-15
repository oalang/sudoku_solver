#!/usr/bin/python3

"""
Solves one of 10000 sample sudoku problems in puzzles.txt.
"""

from linecache import getline

from sudoku import Puzzle

_PUZZLE_SIZE = 9


def main():
    # Prompt user for puzzle number
    puzzle_number = 0
    while puzzle_number < 1 or puzzle_number > 10000:
        puzzle_number = int(input("Choose a puzzle number (1-10000): "))

    # Get puzzle clues
    clues = [[0 for _ in range(_PUZZLE_SIZE)] for _ in range(_PUZZLE_SIZE)]
    for i, num in enumerate(getline('puzzles.txt', puzzle_number).rstrip()):
        clues[i // _PUZZLE_SIZE][i % _PUZZLE_SIZE] = int(num)

    # Build puzzle
    puzzle = Puzzle(clues)

    # Display puzzle
    print()
    print("Puzzle:")
    puzzle.display()

    # Check puzzle validity
    if not puzzle.is_valid():
        print("This puzzle is invalid due to conflicting clues.")
        return

    # Solve puzzle
    puzzle.solve()

    # Check solution validity
    if not puzzle.is_solved():
        print("The search algorithm could not find a valid solution for this puzzle.")
        return

    # Display solution
    print()
    print("Solution:")
    puzzle.display()


if __name__ == '__main__':
    main()
