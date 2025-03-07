# sudoku_logic.py
import json
from random import randint, shuffle
import copy

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
    """
    Solve the Sudoku board using backtracking.
    Returns True if a solution is found, False otherwise.
    """
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
    # Create a deep copy of the board to prevent modifications to the original
    board_copy = copy.deepcopy(board)
    solutions = [0]
    
    def backtrack():
        if solutions[0] >= limit:
            return
            
        empty = find_empty(board_copy)
        if not empty:
            solutions[0] += 1
            return
            
        row, col = empty
        for num in range(1, 10):
            if valid(board_copy, (row, col), num):
                board_copy[row][col] = num
                backtrack()
                if solutions[0] >= limit:
                    return
                board_copy[row][col] = 0
    
    backtrack()
    return solutions[0]

def is_fully_solvable(board):
    """Check if the board has exactly one solution"""
    # Make a deep copy as solve() modifies the input board
    board_copy = copy.deepcopy(board)
    
    # Check if the board can be solved
    if not solve(board_copy):
        return False
    
    # Check that the board has exactly one solution
    return count_solutions(board) == 1

def generate_board(difficulty='medium'):
    """
    Generate a Sudoku board with the specified difficulty.
    Difficulty levels: 'easy', 'medium', 'hard'
    Returns a board with exactly one solution.
    """
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
    if not solve(board):
        # This shouldn't happen, but if it does, try again with a different starting board
        return generate_board(difficulty)
    
    # Create a copy of the solved board
    solution = [row[:] for row in board]
    
    # Set target filled cells based on difficulty
    # Adjusted to create more solvable puzzles
    if difficulty == 'easy':
        target_filled = randint(40, 45)  # More filled cells = easier
    elif difficulty == 'medium':
        target_filled = randint(35, 39)
    else:  # 'hard'
        target_filled = randint(30, 34)  # Fewer filled cells = harder
    
    # Define how many cells we want to remove
    cells_to_remove = 81 - target_filled
    
    # Get all cell positions and shuffle them
    all_cells = [(i, j) for i in range(9) for j in range(9)]
    shuffle(all_cells)
    
    # Remove cells one by one, ensuring we maintain a unique solution
    removed = 0
    for i, j in all_cells:
        # Skip if we've already removed enough cells
        if removed >= cells_to_remove:
            break
            
        # Remember the value before removing
        temp = board[i][j]
        board[i][j] = 0
        
        # Check if board still has exactly one solution
        if count_solutions(board) != 1:
            # If not, restore the cell
            board[i][j] = temp
        else:
            removed += 1
    
    # Final validation - ensure no duplicate numbers in rows, columns or boxes
    for i in range(9):
        # Check rows
        row_vals = [board[i][j] for j in range(9) if board[i][j] != 0]
        if len(row_vals) != len(set(row_vals)):
            # Found duplicates, regenerate
            return generate_board(difficulty)
            
        # Check columns
        col_vals = [board[j][i] for j in range(9) if board[j][i] != 0]
        if len(col_vals) != len(set(col_vals)):
            # Found duplicates, regenerate
            return generate_board(difficulty)
    
    # Check 3x3 boxes
    for box_i in range(3):
        for box_j in range(3):
            box_vals = []
            for i in range(3):
                for j in range(3):
                    val = board[box_i*3 + i][box_j*3 + j]
                    if val != 0:
                        box_vals.append(val)
            if len(box_vals) != len(set(box_vals)):
                # Found duplicates, regenerate
                return generate_board(difficulty)
    
    # Make sure the board is solvable
    test_board = copy.deepcopy(board)
    if not solve(test_board):
        # This shouldn't happen given our checks, but just in case
        return generate_board(difficulty)
        
    return board

def board_to_string(board):
    """Convert board to JSON string."""
    return json.dumps(board)

def string_to_board(board_str):
    """Convert JSON string back to board."""
    return json.loads(board_str)

def is_valid_board(board):
    """Check if a board is valid (follows Sudoku rules)"""
    # Check each row
    for row in range(9):
        nums = {}
        for col in range(9):
            val = board[row][col]
            if val != 0:
                if val in nums:
                    return False  # Duplicate in row
                nums[val] = True
    
    # Check each column
    for col in range(9):
        nums = {}
        for row in range(9):
            val = board[row][col]
            if val != 0:
                if val in nums:
                    return False  # Duplicate in column
                nums[val] = True
    
    # Check each 3x3 box
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            nums = {}
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    val = board[row][col]
                    if val != 0:
                        if val in nums:
                            return False  # Duplicate in box
                        nums[val] = True
    
    return True