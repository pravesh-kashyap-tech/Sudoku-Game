#!/usr/bin/env python3
"""
Sudoku Game (Console)
- Generates a valid Sudoku puzzle with a unique solution
- Difficulty: easy / medium / hard
- Commands:
    place r c n   -> place number n at row r, col c (1-9)
    erase r c     -> erase cell at row r, col c
    hint          -> fill one safe move
    check         -> verify current board validity
    solve         -> show/finish the full solution
    quit          -> abandon current game
    (Numeric shortcuts also supported: 1 3 5 9, 2 1 2, etc.)
"""

import random
import copy
import os
from typing import List, Tuple, Optional

Board = List[List[int]]

def clr():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board(board: Board, fixed: Board | None = None):
    def cell_str(r, c):
        val = board[r][c]
        return f" {val} " if val != 0 else " . "

    print("    C1 C2 C3  C4 C5 C6  C7 C8 C9")
    print("   " + "-"*33)
    for r in range(9):
        row_cells = []
        for c in range(9):
            row_cells.append(cell_str(r, c))
            if c in (2, 5):
                row_cells.append("|")
        row_str = "".join(row_cells)
        print(f"R{r+1} |{row_str}")
        if r in (2, 5):
            print("   " + "-"*33)
    print()


def find_empty(board: Board) -> Optional[Tuple[int, int]]:
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def is_valid(board: Board, r: int, c: int, n: int) -> bool:
    if any(board[r][x] == n for x in range(9)): return False
    if any(board[x][c] == n for x in range(9)): return False
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if board[rr][cc] == n:
                return False
    return True

def solver(board: Board, count_solutions: bool = False, limit: int = 2) -> bool | int:
    empty = find_empty(board)
    if not empty:
        return 1 if count_solutions else True
    r, c = empty

    nums = list(range(1, 10))
    random.shuffle(nums)
    total = 0
    for n in nums:
        if is_valid(board, r, c, n):
            board[r][c] = n
            res = solver(board, count_solutions, limit)
            if count_solutions:
                total += res
                if total >= limit:
                    board[r][c] = 0
                    return total
            else:
                if res:
                    return True
            board[r][c] = 0
    return total if count_solutions else False

def generate_full_board() -> Board:
    board = [[0]*9 for _ in range(9)]
    for box in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        idx = 0
        for r in range(box, box+3):
            for c in range(box, box+3):
                board[r][c] = nums[idx]; idx += 1
    solver(board)
    return board

def unique_solution(board: Board) -> bool:
    temp = copy.deepcopy(board)
    solutions = solver(temp, count_solutions=True, limit=2)
    return solutions == 1

def remove_cells_for_puzzle(sol: Board, clues: int) -> Board:
    puzzle = copy.deepcopy(sol)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    blanks_target = 81 - max(17, min(80, clues))
    removed = 0

    for r, c in cells:
        if removed >= blanks_target:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if not unique_solution(puzzle):
            puzzle[r][c] = saved
        else:
            removed += 1
    return puzzle

def make_puzzle(difficulty: str) -> Tuple[Board, Board]:
    diff = difficulty.lower().strip()
    if diff not in ("easy", "medium", "hard"):
        diff = "easy"
    clue_map = {"easy": 40, "medium": 32, "hard": 26}
    clues = clue_map[diff]

    full = generate_full_board()
    puzzle = remove_cells_for_puzzle(full, clues)
    return puzzle, full

def board_valid_now(board: Board) -> bool:
    for r in range(9):
        seen = set()
        for c in range(9):
            v = board[r][c]
            if v == 0: continue
            if v in seen: return False
            seen.add(v)
    for c in range(9):
        seen = set()
        for r in range(9):
            v = board[r][c]
            if v == 0: continue
            if v in seen: return False
            seen.add(v)
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            seen = set()
            for r in range(br, br+3):
                for c in range(bc, bc+3):
                    v = board[r][c]
                    if v == 0: continue
                    if v in seen: return False
                    seen.add(v)
    return True

# --------- Game Logic ---------

def game():
    clr()
    print("🧩 Welcome to Sudoku!")
    diff_input = input("Choose difficulty: Easy (E) / Medium (M) / Hard (H): ").strip().lower()
    diff_map = {'e': 'easy', 'm': 'medium', 'h': 'hard'}
    diff = diff_map.get(diff_input, 'easy')

    print("\nGenerating puzzle... (this can take a few seconds)")
    puzzle, solution = make_puzzle(diff)

    fixed = [[puzzle[r][c] for c in range(9)] for r in range(9)]
    board = copy.deepcopy(puzzle)

    while True:
        clr()
        print(f"Difficulty: {diff.capitalize()}")
        print_board(board, fixed=fixed)

        if board == solution:
            print("🎉 Congratulations! You solved the Sudoku!")
            break

        print("\n📋 Commands Menu:")
        print("  1 R C N  → Place number n at row r, column c")
        print("  2 R C    → Erase number at row r, column c")
        print("  3        → Hint (fill one safe move)")
        print("  4        → Check board for rule violations")
        print("  5        → Solve (show the full solution)")
        print("  6        → Quit the game")
        cmd = input("> ").strip().lower()


        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0]

        # Numeric shortcuts support
        if action == "1" and len(parts) == 4:
            parts = ["place"] + parts[1:]
            action = "place"
        elif action == "2" and len(parts) == 3:
            parts = ["erase"] + parts[1:]
            action = "erase"
        elif action == "3" and len(parts) == 1:
            parts = ["hint"]
            action = "hint"
        elif action == "4" and len(parts) == 1:
            parts = ["check"]
            action = "check"
        elif action == "5" and len(parts) == 1:
            parts = ["solve"]
            action = "solve"
        elif action == "6" and len(parts) == 1:
            parts = ["quit"]
            action = "quit"

        if action == "place" and len(parts) == 4:
            try:
                r, c, n = int(parts[1])-1, int(parts[2])-1, int(parts[3])
                if not (0 <= r < 9 and 0 <= c < 9 and 1 <= n <= 9):
                    print("⚠️ Use ranges: r,c in 1..9 and n in 1..9")
                    input("Press Enter...")
                    continue
                if fixed[r][c] != 0:
                    print("⚠️ That cell is a fixed clue; cannot edit.")
                    input("Press Enter...")
                    continue
                if not is_valid(board, r, c, n):
                    print("❌ Not valid by Sudoku rules for current board.")
                    input("Press Enter...")
                    continue
                board[r][c] = n
            except ValueError:
                print("⚠️ Usage: place r c n  (numbers)")
                input("Press Enter...")

        elif action == "erase" and len(parts) == 3:
            try:
                r, c = int(parts[1])-1, int(parts[2])-1
                if not (0 <= r < 9 and 0 <= c < 9):
                    print("⚠️ r,c must be 1..9")
                    input("Press Enter...")
                    continue
                if fixed[r][c] != 0:
                    print("⚠️ Cannot erase a fixed clue.")
                    input("Press Enter...")
                    continue
                board[r][c] = 0
            except ValueError:
                print("⚠️ Usage: erase r c")
                input("Press Enter...")

        elif action == "hint":
            empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
            if not empties:
                print("No empty cells for hint!")
                input("Press Enter...")
                continue
            r, c = random.choice(empties)
            board[r][c] = solution[r][c]
            print(f"💡 Hint: R{r+1} C{c+1} = {solution[r][c]}")
            input("Press Enter...")

        elif action == "check":
            ok = board_valid_now(board)
            print("✔️ Board is valid so far." if ok else "❌ Board has rule violations.")
            input("Press Enter...")

        elif action == "solve":
            clr()
            print("Here is the solution:")
            print_board(solution, fixed=solution)
            input("Press Enter to return...")
            break

        elif action == "quit":
            print("👋 Quitting current game.")
            break

        else:
            print("❓ Unknown command.")
            input("Press Enter...")

def main():
    while True:
        game()
        again = input("\nPlay again? (yes/no): ").strip().lower()
        if again != "yes":
            print("Thanks for playing Sudoku! 👋")
            break

if __name__ == "__main__":
    main()
