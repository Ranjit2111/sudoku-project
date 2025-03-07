# frontend.py
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, ttk
import requests
import json
import sys
from sudoku_logic import generate_board, solve, board_to_string, string_to_board, is_valid_board, count_solutions
import copy

API_URL = "http://localhost:5000"

def check_backend_connection():
    try:
        requests.get(API_URL, timeout=2)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku - Play & Solve")
        self.root.geometry("600x700")
        self.user_id = None
        self.board = None
        self.original_board = None  # Store the original board state
        self.entries = []
        self.current_focus = None  # Track current selected cell
        self.hints_used = 0  # Track hints used in current game
        self.solved_by_algorithm = False  # Track if solve button was used
        self.user_stats = {"puzzles_played": 0, "puzzles_solved": 0, "win_percentage": 0}
        
        # Check backend connection before proceeding
        if not check_backend_connection():
            messagebox.showerror("Connection Error", 
                                "Cannot connect to the backend server. Please restart the application.")
            root.after(1000, root.destroy)
            return
            
        self.create_login_screen()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_login_screen(self):
        self.clear_root()
        frame = tk.Frame(self.root)
        frame.pack(pady=50)

        title = tk.Label(frame, text="Sudoku Solver", font=("Helvetica", 28, "bold"), fg="#2E86C1")
        title.pack(pady=10)

        form_frame = tk.Frame(frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Username:", font=("Helvetica", 16)).grid(row=0, column=0, pady=5, padx=5, sticky="e")
        self.username_entry = tk.Entry(form_frame, font=("Helvetica", 16))
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Password:", font=("Helvetica", 16)).grid(row=1, column=0, pady=5, padx=5, sticky="e")
        self.password_entry = tk.Entry(form_frame, font=("Helvetica", 16), show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Login", font=("Helvetica", 16), command=self.login, bg="#28B463", fg="white").grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Sign Up", font=("Helvetica", 16), command=self.register, bg="#F39C12", fg="white").grid(row=0, column=1, padx=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        try:
            response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                self.user_id = data["user_id"]
                # Load user statistics from login response
                if "stats" in data:
                    self.user_stats = data["stats"]
                self.create_game_screen()
            else:
                messagebox.showerror("Login Failed", response.json().get("message", "Error logging in"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to backend. {e}")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long.")
            return
        try:
            response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
            if response.status_code == 200:
                messagebox.showinfo("Success", "Registration successful! Please login.")
            else:
                messagebox.showerror("Error", response.json().get("message", "Registration failed"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to backend. {e}")

    def create_game_screen(self):
        self.clear_root()
        
        # Attempt to load a saved game; if none, generate a new one
        loaded_game = self.load_saved_game()
        if loaded_game:
            self.board = loaded_game["board_state"]
            self.original_board = loaded_game["original_board"]
            self.hints_used = loaded_game.get("hints_used", 0)
            self.solved_by_algorithm = loaded_game.get("solved_by_algorithm", False)
        else:
            # Generate a new board with enough empty cells
            self.board = self.generate_playable_board()
            self.original_board = [[cell for cell in row] for row in self.board]
            self.hints_used = 0
            self.solved_by_algorithm = False
        
        # Create a frame for user stats display
        stats_frame = tk.Frame(self.root)
        stats_frame.pack(pady=5)
        stats_text = f"Games Played: {self.user_stats['puzzles_played']} | Games Won: {self.user_stats['puzzles_solved']} | Win Rate: {self.user_stats['win_percentage']:.1f}%"
        tk.Label(stats_frame, text=stats_text, font=("Helvetica", 12)).pack()
        
        # Create Sudoku board grid
        self.entries = []
        board_frame = tk.Frame(self.root)
        board_frame.pack(pady=10)
        
        # Create a grid for the Sudoku board with visual separation for 3x3 boxes
        for i in range(9):
            row_entries = []
            for j in range(9):
                # Add thicker borders for 3x3 box separation
                border_thickness = 1
                if i % 3 == 0 and i > 0:
                    border_thickness = 3
                if j % 3 == 0 and j > 0:
                    border_thickness = 3
                
                e = tk.Entry(board_frame, width=2, font=("Helvetica", 20), justify="center", 
                           bd=border_thickness, relief="ridge")
                e.grid(row=i, column=j, padx=1, pady=1)
                
                # Set focus tracking for hint feature
                e.bind("<FocusIn>", lambda event, row=i, col=j: self.update_focus(row, col))
                
                # Populate the board
                if self.board[i][j] != 0:
                    e.insert(0, str(self.board[i][j]))
                    # Distinguish between original cells and user/hint filled cells
                    if self.original_board[i][j] != 0:
                        e.config(state="disabled", disabledforeground="black")
                    else:
                        # Apply highlight for hints if the board was loaded with hints
                        e.config(bg="#D4E6F1")
                row_entries.append(e)
            self.entries.append(row_entries)
            
        # Game info display
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        self.hints_label = tk.Label(info_frame, text=f"Hints Used: {self.hints_used}/2", font=("Helvetica", 12))
        self.hints_label.pack()
            
        # Buttons for game options (first row)
        btn_frame1 = tk.Frame(self.root)
        btn_frame1.pack(pady=5)
        tk.Button(btn_frame1, text="Hint", font=("Helvetica", 14), command=self.hint, bg="#3498DB", fg="white", width=8).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame1, text="Reset", font=("Helvetica", 14), command=self.reset_board, bg="#E74C3C", fg="white", width=8).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame1, text="Solve", font=("Helvetica", 14), command=self.solve_board, bg="#1ABC9C", fg="white", width=8).grid(row=0, column=2, padx=5)
        
        # Buttons for game options (second row)
        btn_frame2 = tk.Frame(self.root)
        btn_frame2.pack(pady=5)
        tk.Button(btn_frame2, text="New Game", font=("Helvetica", 14), command=self.new_game, bg="#2ECC71", fg="white", width=8).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame2, text="Leaderboard", font=("Helvetica", 14), command=self.show_leaderboard, bg="#9B59B6", fg="white", width=10).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame2, text="Logout", font=("Helvetica", 14), command=self.logout, bg="#7D3C98", fg="white", width=8).grid(row=0, column=2, padx=5)
        
        # Check solution button
        tk.Button(self.root, text="Check Solution", font=("Helvetica", 16), command=self.check_solution, bg="#F39C12", fg="white", width=15).pack(pady=10)
        
        # Ensure game state is saved when closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_focus(self, row, col):
        """Track the currently focused cell for targeted hints"""
        self.current_focus = (row, col)

    def generate_playable_board(self):
        """Generate a board with a guaranteed single solution"""
        # We'll use the improved generate_board function from sudoku_logic
        # The improved function already ensures a valid board with a single solution
        difficulties = ['easy', 'medium', 'hard']
        selected_difficulty = difficulties[1]  # Default to medium difficulty
        
        # Generate board using the improved function in sudoku_logic.py
        board = None
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                board = generate_board(difficulty=selected_difficulty)
                # Verify the board has exactly one solution and is valid
                board_copy = copy.deepcopy(board)
                if solve(board_copy) and count_solutions(board) == 1:
                    return board
            except Exception:
                pass  # Try again if any error occurs
            attempt += 1
            
        # If we had trouble generating a board, try with 'easy' difficulty as fallback
        return generate_board(difficulty='easy')

    def new_game(self):
        """Create a new game board and update the UI"""
        if messagebox.askyesno("New Game", "Are you sure you want to start a new game? Your current progress will be lost."):
            # Delete current game from the backend
            try:
                if self.user_id:
                    requests.delete(f"{API_URL}/delete_game/{self.user_id}")
            except Exception:
                pass  # Ignore errors here
            
            # Generate a new board and refresh the UI
            self.board = self.generate_playable_board()
            self.original_board = [[cell for cell in row] for row in self.board]
            self.hints_used = 0
            self.solved_by_algorithm = False
            
            # Save the new game with is_new_game flag set to True to increment the counter
            try:
                requests.post(f"{API_URL}/save_game", json={
                    "user_id": self.user_id,
                    "board_state": json.dumps(self.board),
                    "original_board": json.dumps(self.original_board),
                    "completed": False,
                    "hints_used": 0,
                    "solved_by_algorithm": False,
                    "is_new_game": True
                })
                
                # Update the local counter for display
                self.user_stats['puzzles_played'] += 1
            except Exception as e:
                messagebox.showerror("Error", f"Could not create new game: {e}")
                
            self.create_game_screen()

    def reset_board(self):
        """Reset the current board to its original state"""
        if messagebox.askyesno("Reset Game", "Are you sure you want to reset the current game to its original state?"):
            for i in range(9):
                for j in range(9):
                    # Clear all user-editable entries
                    if self.original_board[i][j] == 0:
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].config(bg="white")  # Reset background color
                    
            # Keep track of hints but reset color highlighting
            # Don't reset hints_used counter as those have already been counted
            self.save_game()

    def load_saved_game(self):
        try:
            response = requests.get(f"{API_URL}/load_game/{self.user_id}")
            if response.status_code == 200:
                data = response.json()
                if "board_state" in data and "original_board" in data:
                    result = {
                        "board_state": json.loads(data["board_state"]),
                        "original_board": json.loads(data["original_board"]),
                        "hints_used": data.get("hints_used", 0),
                        "solved_by_algorithm": data.get("solved_by_algorithm", False)
                    }
                    return result
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Could not load saved game. {e}")
            return None

    def save_game(self, completed=False):
        if self.user_id is None or self.board is None:
            return
        
        # Update board from entry fields
        current_board = []
        for i in range(9):
            row = []
            for j in range(9):
                entry_value = self.entries[i][j].get()
                try:
                    val = int(entry_value) if entry_value else 0
                    if val < 0 or val > 9:
                        val = 0
                except ValueError:
                    val = 0
                row.append(val)
            current_board.append(row)
        
        try:
            response = requests.post(f"{API_URL}/save_game", json={
                "user_id": self.user_id,
                "board_state": json.dumps(current_board),
                "original_board": json.dumps(self.original_board),
                "completed": completed,
                "hints_used": self.hints_used,
                "solved_by_algorithm": self.solved_by_algorithm
            })
            
            if response.status_code != 200:
                messagebox.showerror("Error", f"Failed to save game: {response.json().get('message', 'Unknown error')}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not save game. {e}")

    def hint(self):
        # Check if hints limit reached
        if self.hints_used >= 2:
            messagebox.showinfo("Hint Limit", "You've already used 2 hints. Using more will affect your ability to win this game.")
        
        # Increase hint counter and update display
        self.hints_used += 1
        self.hints_label.config(text=f"Hints Used: {self.hints_used}/2")
        
        # Get current board state
        current_board = []
        for i in range(9):
            row = []
            for j in range(9):
                entry_value = self.entries[i][j].get()
                try:
                    val = int(entry_value) if entry_value else 0
                except ValueError:
                    val = 0
                row.append(val)
            current_board.append(row)
        
        # Check if the current board is valid before attempting to solve
        if not is_valid_board(current_board):
            messagebox.showerror("Invalid Board", "The current board has conflicts (duplicate numbers). Please fix them first.")
            # Revert the hint counter since we didn't actually use a hint
            self.hints_used -= 1
            self.hints_label.config(text=f"Hints Used: {self.hints_used}/2")
            return
            
        # Create a copy of the board for solving
        solution_board = copy.deepcopy(current_board)
        if solve(solution_board):
            # If a cell is focused, provide hint for that specific cell
            if self.current_focus:
                row, col = self.current_focus
                if current_board[row][col] == 0:  # Only provide hint if cell is empty
                    correct_val = solution_board[row][col]
                    self.entries[row][col].delete(0, tk.END)
                    self.entries[row][col].insert(0, str(correct_val))
                    self.entries[row][col].config(bg="#D4E6F1")  # Light blue background for hints
                    self.save_game()
                    return
                else:
                    messagebox.showinfo("Hint", "This cell is already filled. Please select an empty cell.")
                    # Revert the hint counter since we didn't actually use a hint
                    self.hints_used -= 1
                    self.hints_label.config(text=f"Hints Used: {self.hints_used}/2")
                    return
            
            # If no cell is focused, find first empty cell
            for i in range(9):
                for j in range(9):
                    if current_board[i][j] == 0:
                        correct_val = solution_board[i][j]
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(correct_val))
                        self.entries[i][j].config(bg="#D4E6F1")  # Light blue background for hints
                        self.save_game()
                        return
                        
            messagebox.showinfo("Hint", "No empty cells available for a hint.")
            # Revert the hint counter
            self.hints_used -= 1
            self.hints_label.config(text=f"Hints Used: {self.hints_used}/2")
        else:
            # Revert the hint counter since we couldn't provide a hint
            self.hints_used -= 1
            self.hints_label.config(text=f"Hints Used: {self.hints_used}/2")
            
            # Attempt to identify the cause of the error
            if not is_valid_board(current_board):
                messagebox.showerror("Error", "The current board has conflicts. Please check for duplicate numbers in rows, columns, or 3x3 boxes.")
            else:
                messagebox.showerror("Error", "Unable to compute hint. The current board configuration may not have a valid solution.")

    def check_solution(self):
        """Check if the current board state is correct"""
        current_board = []
        for i in range(9):
            row = []
            for j in range(9):
                entry_value = self.entries[i][j].get()
                try:
                    val = int(entry_value) if entry_value else 0
                except ValueError:
                    val = 0
                row.append(val)
            current_board.append(row)
        
        # First check if the board is filled
        is_filled = all(current_board[i][j] != 0 for i in range(9) for j in range(9))
        if not is_filled:
            messagebox.showinfo("Incomplete", "The board is not completely filled.")
            return
            
        # Check if the solution is valid
        if is_valid_board(current_board):
            # Determine if this counts as a valid win (≤2 hints and no solve button)
            valid_win = self.hints_used <= 2 and not self.solved_by_algorithm
            
            if valid_win:
                messagebox.showinfo("Correct", "Congratulations! Your solution is correct. This counts as a win!")
            else:
                reason = ""
                if self.hints_used > 2:
                    reason = "You used more than 2 hints."
                elif self.solved_by_algorithm:
                    reason = "You used the solve button."
                
                messagebox.showinfo("Correct", f"Your solution is correct, but it doesn't count as a win because {reason}")
            
            # Save the completed game with win status
            self.save_game(completed=True)
            
            # Ask if user wants to start a new game
            if messagebox.askyesno("New Game", "Would you like to start a new game?"):
                self.new_game()
        else:
            messagebox.showinfo("Incorrect", "Your solution contains errors. Please check and try again.")

    def solve_board(self):
        # Get current board state
        current_board = []
        for i in range(9):
            row = []
            for j in range(9):
                entry_value = self.entries[i][j].get()
                try:
                    val = int(entry_value) if entry_value else 0
                except ValueError:
                    val = 0
                row.append(val)
            current_board.append(row)
            
        # Check if the current board is valid before attempting to solve
        if not is_valid_board(current_board):
            messagebox.showerror("Invalid Board", "The current board has conflicts (duplicate numbers). Please fix them first.")
            return
            
        # Create a copy for solving to avoid modifying the original
        solution_board = copy.deepcopy(current_board)
        
        if solve(solution_board):
            # Mark that the solve algorithm was used
            self.solved_by_algorithm = True
            
            # Update the board with the solution
            for i in range(9):
                for j in range(9):
                    if self.original_board[i][j] == 0:  # Only update non-original cells
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(solution_board[i][j]))
                        self.entries[i][j].config(bg="#ABEBC6")  # Light green for solved cells
            
            self.save_game(completed=True)
            messagebox.showinfo("Solved", "Puzzle solved! Note that using the solve button means this won't count as a win.")
        else:
            # Attempt to identify the cause of the error
            if not is_valid_board(current_board):
                messagebox.showerror("Error", "The current board has conflicts. Please check for duplicate numbers in rows, columns, or 3x3 boxes.")
            else:
                messagebox.showerror("Error", "No solution exists for the current board. There might be a mistake in the entries.")

    def show_leaderboard(self):
        """Display leaderboard in a new window"""
        try:
            response = requests.get(f"{API_URL}/leaderboard")
            if response.status_code == 200:
                leaderboard_data = response.json().get("leaderboard", [])
                
                # Create a new window for the leaderboard
                lb_window = Toplevel(self.root)
                lb_window.title("Sudoku Leaderboard")
                lb_window.geometry("500x400")
                
                # Header
                tk.Label(lb_window, text="Leaderboard", font=("Helvetica", 18, "bold")).pack(pady=10)
                
                # Create treeview for tabular display
                columns = ("Rank", "Username", "Games Played", "Games Won", "Win %")
                tree = ttk.Treeview(lb_window, columns=columns, show="headings", height=15)
                
                for col in columns:
                    tree.heading(col, text=col)
                    # Adjust column widths
                    if col == "Username":
                        tree.column(col, width=150)
                    else:
                        tree.column(col, width=80, anchor="center")
                
                # Add scrollbar
                scrollbar = ttk.Scrollbar(lb_window, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y")
                tree.pack(expand=True, fill="both", padx=10, pady=10)
                
                # Populate data
                for i, user in enumerate(leaderboard_data):
                    tree.insert("", "end", values=(
                        i + 1,
                        user["username"],
                        user["puzzles_played"],
                        user["puzzles_solved"],
                        f"{user['win_percentage']}%"
                    ))
                
                # Close button
                tk.Button(lb_window, text="Close", command=lb_window.destroy, 
                          font=("Helvetica", 12), bg="#E74C3C", fg="white").pack(pady=10)
                
            else:
                messagebox.showerror("Error", "Failed to fetch leaderboard data.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load leaderboard: {e}")

    def logout(self):
        self.save_game()
        self.user_id = None
        self.board = None
        self.create_login_screen()

    def on_close(self):
        self.save_game()
        self.root.destroy()

def run_frontend():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_frontend()
