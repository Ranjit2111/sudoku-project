# sudoku_logic.py
import json
from random import randint, shuffle

def print_board(board):
    for row in board:
        print(" ".join(str(cell) if cell != 0 else "." for cell in row))

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def valid(board, pos, num):
    # Check row
    for j in range(9):
        if board[pos[0]][j] == num and j != pos[1]:
            return False
            
    # Check column    
    for i in range(9):
        if board[i][pos[1]] == num and i != pos[0]:
            return False
            
    # Check 3x3 box
    box_row, box_col = pos[0] // 3 * 3, pos[1] // 3 * 3
    for i in range(3):
        for j in range(3):
            r, c = box_row + i, box_col + j
            if board[r][c] == num and (r, c) != pos:
                return False
                
    return True

def solve(board):
    empty = find_empty(board)
    if not empty:
        return True
    row, col = empty
    
    # Try numbers 1-9 in a random order to add variety
    nums = list(range(1, 10))
    shuffle(nums)
    
    for num in nums:
        if valid(board, (row, col), num):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0  # Backtrack if no solution
    return False

def count_solutions(board, limit=2):
    """Count the number of solutions a board has, up to the limit"""
    solutions = [0]
    
    def backtrack():
        if solutions[0] >= limit:
            return
            
        empty = find_empty(board)
        if not empty:
            solutions[0] += 1
            return
            
        row, col = empty
        for num in range(1, 10):
            if valid(board, (row, col), num):
                board[row][col] = num
                backtrack()
                if solutions[0] >= limit:
                    return
                board[row][col] = 0
    
    backtrack()
    return solutions[0]

def generate_board():
    # Start with an empty board
    board = [[0 for _ in range(9)] for _ in range(9)]
    
    # Fill each diagonal 3x3 block (which don't affect each other)
    for i in range(0, 9, 3):
        nums = list(range(1, 10))
        shuffle(nums)
        for row in range(3):
            for col in range(3):
                board[i + row][i + col] = nums.pop()
    
    # Solve the rest of the board
    solve(board)
    
    # Create a copy of the solved board
    solution = [row[:] for row in board]
    
    # Remove cells to create the puzzle
    # We'll use a more sophisticated approach to ensure unique solution
    cells = [(i, j) for i in range(9) for j in range(9)]
    shuffle(cells)
    
    # First, remove a significant number of cells quickly
    # Keep around 30 cells filled initially (81-51)
    for i, j in cells[:51]:
        temp = board[i][j]
        board[i][j] = 0
        
    # Then carefully remove more cells while ensuring unique solution
    for i, j in cells[51:]:
        temp = board[i][j]
        board[i][j] = 0
        
        # If removing this cell creates multiple solutions, put it back
        if count_solutions(board) > 1:
            board[i][j] = temp
            
        # Stop when we've reached the desired difficulty level
        filled_cells = sum(1 for row in board for cell in row if cell != 0)
        if filled_cells <= 25:  # Aim for around 25 filled cells for a challenging puzzle
            break
    
    return board

def board_to_string(board):
    """Convert board to JSON string."""
    return json.dumps(board)

def string_to_board(board_str):
    """Convert JSON string back to board."""
    return json.loads(board_str)

def is_valid_board(board):
    """Check if a board is valid (follows Sudoku rules)"""
    # Check each position in the board
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:  # Skip empty cells
                # Temporarily set the cell to 0 to check validity
                temp = board[i][j]
                board[i][j] = 0
                if not valid(board, (i, j), temp):
                    board[i][j] = temp  # Restore value
                    return False
                board[i][j] = temp  # Restore value
    return True
