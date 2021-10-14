#!/usr/bin/python3

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

    clues = [[1, 0, 0, 0, 0, 7, 0, 9, 0],
             [0, 3, 0, 0, 2, 0, 0, 0, 8],
             [0, 0, 9, 6, 0, 0, 5, 0, 0],
             [0, 0, 5, 3, 0, 0, 9, 0, 0],
             [0, 1, 0, 0, 8, 0, 0, 0, 2],
             [6, 0, 0, 0, 0, 4, 0, 0, 0],
             [3, 0, 0, 0, 0, 0, 0, 1, 0],
             [0, 4, 1, 0, 0, 0, 0, 0, 7],
             [0, 0, 7, 0, 0, 0, 3, 0, 0]]


    # Build puzzle
    puzzle = Puzzle(clues)

    # Display puzzle
    print("Puzzle:")
    puzzle.display()
    print()

    if not puzzle.is_valid():
        print("This puzzle is invalid due to conflicting clues.")
        return

    # Solve puzzle
    puzzle.solve()

    if not puzzle.is_solved():
        print("The search algorithm could not find a solution for this puzzle.")
        return

    # Display solution
    print("Solution:")
    puzzle.display()
    print()


if __name__ == '__main__':
    main()
