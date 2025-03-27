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
        # Set nice background color for the entire application
        self.root.configure(bg="#EBF5FB")  # Light blue background
        
        # Define color scheme for the application
        self.colors = {
            "primary": "#3498DB",  # Blue
            "secondary": "#2ECC71",  # Green
            "accent": "#9B59B6",  # Purple
            "warning": "#E74C3C",  # Red
            "info": "#F39C12",  # Orange
            "light": "#F8F9F9",  # Light gray
            "dark": "#2C3E50",  # Dark blue/gray
            "white": "#FFFFFF",
            "cell_original": "#F8F9F9",  # Light gray for original cells
            "cell_user": "#D6EAF8",  # Very light blue for user entries
            "cell_hint": "#D4E6F1",  # Light blue for hints
            "cell_solved": "#ABEBC6",  # Light green for solved cells
            "cell_border": "#95A5A6",  # Gray for cell borders
            "cell_selected": "#D6DBDF"  # Gray for selected cell
        }
        
        self.user_id = None
        self.board = None
        self.original_board = None  # Store the original board state
        self.entries = []
        self.current_focus = None  # Track current selected cell
        self.hints_used = 0  # Track hints used in current game
        self.solved_by_algorithm = False  # Track if solve button was used
        self.user_stats = {"puzzles_played": 0, "puzzles_solved": 0, "win_percentage": 0}
        self.time_remaining = 30 * 60  # 30 minutes in seconds
        self.timer_running = False
        self.time_expired = False
        
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
        self.root.configure(bg="#EBF5FB")  # Apply background to login screen
        
        frame = tk.Frame(self.root, bg="#EBF5FB")
        frame.pack(pady=50)

        # App logo/title with shadow effect
        title = tk.Label(frame, text="Sudoku", font=("Helvetica", 40, "bold"), 
                         fg=self.colors["primary"], bg="#EBF5FB")
        title.pack(pady=5)
        subtitle = tk.Label(frame, text="Play & Solve", font=("Helvetica", 18), 
                           fg=self.colors["dark"], bg="#EBF5FB")
        subtitle.pack(pady=5)

        form_frame = tk.Frame(frame, bg="#EBF5FB", bd=2, relief="solid", padx=20, pady=20)
        form_frame.pack(pady=20)

        tk.Label(form_frame, text="Username:", font=("Helvetica", 16), 
                bg="#EBF5FB", fg=self.colors["dark"]).grid(row=0, column=0, pady=10, padx=5, sticky="e")
        self.username_entry = tk.Entry(form_frame, font=("Helvetica", 16), width=15, bd=2, relief="solid")
        self.username_entry.grid(row=0, column=1, pady=10, padx=5)
        
        # Set focus to username entry
        self.username_entry.focus_set()

        tk.Label(form_frame, text="Password:", font=("Helvetica", 16), 
                bg="#EBF5FB", fg=self.colors["dark"]).grid(row=1, column=0, pady=10, padx=5, sticky="e")
        self.password_entry = tk.Entry(form_frame, font=("Helvetica", 16), show="*", width=15, bd=2, relief="solid")
        self.password_entry.grid(row=1, column=1, pady=10, padx=5)

        button_frame = tk.Frame(form_frame, bg="#EBF5FB")
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        login_btn = tk.Button(button_frame, text="Login", font=("Helvetica", 14, "bold"), 
                            command=self.login, bg=self.colors["primary"], fg="white", 
                            width=8, bd=0, padx=10, pady=5)
        login_btn.grid(row=0, column=0, padx=10)
        
        signup_btn = tk.Button(button_frame, text="Sign Up", font=("Helvetica", 14), 
                             command=self.register, bg=self.colors["secondary"], fg="white", 
                             width=8, bd=0, padx=10, pady=5)
        signup_btn.grid(row=0, column=1, padx=10)
        
        # Bind Enter key to login function
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda event: self.login())
        
        # Bind Shift+Enter to register function for quick signup
        self.password_entry.bind("<Shift-Return>", lambda event: self.register())

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
                self.create_home_screen()  # Go to home screen instead of game screen
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

    def create_home_screen(self):
        """Create a home screen with game options"""
        self.clear_root()
        self.root.configure(bg="#EBF5FB")  # Apply background
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#EBF5FB")
        main_frame.pack(pady=30, fill="both", expand=True)
        
        # Title
        title = tk.Label(main_frame, text="Sudoku", font=("Helvetica", 36, "bold"), 
                        fg=self.colors["primary"], bg="#EBF5FB")
        title.pack(pady=5)
        
        # Welcome header with user statistics
        welcome_frame = tk.Frame(main_frame, bg="#EBF5FB")
        welcome_frame.pack(pady=10, fill="x")
        
        welcome_text = f"Welcome! Games Played: {self.user_stats['puzzles_played']} | Games Won: {self.user_stats['puzzles_solved']} | Win Rate: {self.user_stats['win_percentage']:.1f}%"
        tk.Label(welcome_frame, text=welcome_text, font=("Helvetica", 14), 
                bg="#EBF5FB", fg=self.colors["dark"]).pack(pady=5)
        
        # Logout button in top right
        logout_btn = tk.Button(
            welcome_frame, 
            text="Logout", 
            font=("Helvetica", 12), 
            command=self.logout, 
            bg=self.colors["accent"], 
            fg="white",
            width=8,
            bd=0,
            padx=10,
            pady=5
        )
        logout_btn.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Buttons frame with card-like appearance
        buttons_frame = tk.Frame(main_frame, bg=self.colors["light"], bd=2, relief="solid", padx=30, pady=30)
        buttons_frame.pack(pady=30)
        
        # New Game button (opens difficulty selection)
        new_game_btn = tk.Button(
            buttons_frame,
            text="New Game",
            font=("Helvetica", 16, "bold"),
            command=self.show_difficulty_selection,
            bg=self.colors["secondary"],
            fg="white",
            width=15,
            height=2,
            bd=0
        )
        new_game_btn.pack(pady=15)
        
        # Leaderboard button
        leaderboard_btn = tk.Button(
            buttons_frame,
            text="Leaderboard",
            font=("Helvetica", 16),
            command=self.show_leaderboard,
            bg=self.colors["accent"],
            fg="white",
            width=15,
            height=2,
            bd=0
        )
        leaderboard_btn.pack(pady=15)
        
        # Load last game button (if exists)
        last_game_exists = self.check_saved_game_exists()
        if last_game_exists:
            continue_btn = tk.Button(
                buttons_frame,
                text="Continue Game",
                font=("Helvetica", 16),
                command=lambda: self.create_game_screen(False, True),  # False for new_game, True for continue_game
                bg=self.colors["primary"],
                fg="white",
                width=15,
                height=2,
                bd=0
            )
            continue_btn.pack(pady=15)
            
    def check_saved_game_exists(self):
        """Check if a saved game exists for the current user"""
        try:
            response = requests.get(f"{API_URL}/load_game/{self.user_id}")
            return response.status_code == 200 and "board_state" in response.json()
        except:
            return False
    
    def show_difficulty_selection(self, is_new_game=False):
        """Show difficulty selection dialog"""
        # Create a new top-level window with improved styling
        difficulty_window = Toplevel(self.root)
        difficulty_window.title("Select Difficulty")
        difficulty_window.geometry("300x420")  # Increased height for better display
        difficulty_window.configure(bg="#EBF5FB")  # Apply background
        difficulty_window.transient(self.root)  # Set to be on top of the main window
        difficulty_window.grab_set()  # Modal window
        
        # Center the window
        difficulty_window.update_idletasks()
        width = difficulty_window.winfo_width()
        height = difficulty_window.winfo_height()
        x = (difficulty_window.winfo_screenwidth() // 2) - (width // 2)
        y = (difficulty_window.winfo_screenheight() // 2) - (height // 2)
        difficulty_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Title with attractive styling
        tk.Label(
            difficulty_window, 
            text="Select Difficulty", 
            font=("Helvetica", 22, "bold"),
            fg=self.colors["primary"],
            bg="#EBF5FB"
        ).pack(pady=5)
        
        # Description
        tk.Label(
            difficulty_window,
            text="Choose a difficulty level for your game:",
            font=("Helvetica", 12),
            fg=self.colors["dark"],
            bg="#EBF5FB"
        ).pack(pady=5)
        
        # Main content frame to ensure proper spacing
        content_frame = tk.Frame(difficulty_window, bg="#EBF5FB")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Difficulty levels frame with card-like appearance
        levels_frame = tk.Frame(content_frame, bg=self.colors["light"], 
                              bd=2, relief="solid", padx=10, pady=15)
        levels_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a consistent style for all difficulty buttons
        button_style = {
            "font": ("Helvetica", 14, "bold"),
            "fg": "white",
            "width": 12,
            "height": 2,  # Increased height for better appearance
            "bd": 0,
            "padx": 10,
            "pady": 8
        }
        
        # Easy button with improved styling
        easy_btn = tk.Button(
            levels_frame,
            text="Easy",
            bg=self.colors["secondary"],
            command=lambda: self.start_game_with_difficulty("easy", difficulty_window, is_new_game),
            **button_style
        )
        easy_btn.pack(pady=5)
        
        # Medium button
        medium_btn = tk.Button(
            levels_frame,
            text="Medium",
            bg=self.colors["info"],
            command=lambda: self.start_game_with_difficulty("medium", difficulty_window, is_new_game),
            **button_style
        )
        medium_btn.pack(pady=5)
        
        # Hard button
        hard_btn = tk.Button(
            levels_frame,
            text="Hard",
            bg=self.colors["warning"],
            command=lambda: self.start_game_with_difficulty("hard", difficulty_window, is_new_game),
            **button_style
        )
        hard_btn.pack(pady=5)
    
    def start_game_with_difficulty(self, difficulty, dialog_window, is_new_game):
        """Start a new game with the selected difficulty"""
        # Store the selected difficulty
        self.selected_difficulty = difficulty
        # Close the difficulty selection dialog
        dialog_window.destroy()
        
        # Handle different scenarios
        if is_new_game:
            # We're starting a new game from within an existing game
            if messagebox.askyesno("New Game", "Are you sure you want to start a new game? Your current progress will be lost."):
                self.new_game()
        else:
            # We're starting a game from the home screen
            self.create_game_screen(True)
            
    def create_game_screen(self, new_game=False, continue_game=False):
        self.clear_root()
        self.root.configure(bg="#EBF5FB")  # Apply background
        
        # If continuing a game, force load saved game
        if continue_game:
            loaded_game = self.load_saved_game()
            if loaded_game:
                self.board = loaded_game["board_state"]
                self.original_board = loaded_game["original_board"]
                self.hints_used = loaded_game.get("hints_used", 0)
                self.solved_by_algorithm = loaded_game.get("solved_by_algorithm", False)
                self.time_remaining = loaded_game.get("time_remaining", 30 * 60)
                self.time_expired = loaded_game.get("time_expired", False)
            else:
                # If somehow we can't load the game, go back to the home screen
                messagebox.showerror("Error", "Could not load the saved game.")
                self.create_home_screen()
                return
        # If starting a new game or no saved game exists (and not explicitly continuing)
        elif new_game or not self.load_saved_game():
            # Generate a new board with the selected difficulty
            if hasattr(self, 'selected_difficulty'):
                self.board = self.generate_playable_board(self.selected_difficulty)
            else:
                self.board = self.generate_playable_board("medium")  # Default difficulty
                
            self.original_board = [[cell for cell in row] for row in self.board]
            self.hints_used = 0
            self.solved_by_algorithm = False
            self.time_remaining = 30 * 60  # Reset timer to 30 minutes
            self.time_expired = False
        
            # Save new game with is_new_game flag if it's a new game (not initial load)
            if new_game:
                try:
                    requests.post(f"{API_URL}/save_game", json={
                        "user_id": self.user_id,
                        "board_state": json.dumps(self.board),
                        "original_board": json.dumps(self.original_board),
                        "completed": False,
                        "hints_used": 0,
                        "solved_by_algorithm": False,
                        "time_remaining": self.time_remaining,
                        "time_expired": self.time_expired,
                        "is_new_game": True
                    })
                    
                    # Update the local counter for display
                    self.user_stats['puzzles_played'] += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create new game: {e}")
        
        # Main container frame with cleaner design
        main_container = tk.Frame(self.root, bg="#EBF5FB", padx=15, pady=15)
        main_container.pack(fill="both", expand=True)
        
        # Top stats and logout frame
        top_frame = tk.Frame(main_container, bg="#EBF5FB")
        top_frame.pack(fill="x", pady=5)
        
        # Timer display (top left)
        timer_frame = tk.Frame(top_frame, bg="#EBF5FB")
        timer_frame.pack(side="left", padx=10)
        
        self.timer_label = tk.Label(timer_frame, 
                                    text=self.format_time(self.time_remaining), 
                                    font=("Helvetica", 16, "bold"), 
                                    bg="#EBF5FB", 
                                    fg=self.colors["primary"])
        self.timer_label.pack(side="left")
        
        # Start/restart the timer
        self.start_timer()
        
        # Game title (centered)
        title_frame = tk.Frame(top_frame, bg="#EBF5FB")
        title_frame.pack(side="top", fill="x")
        title = tk.Label(title_frame, text="Sudoku", font=("Helvetica", 22, "bold"), 
                        fg=self.colors["primary"], bg="#EBF5FB")
        title.pack(pady=5)
        
        # Stats display
        stats_text = f"Games Played: {self.user_stats['puzzles_played']} | Games Won: {self.user_stats['puzzles_solved']} | Win Rate: {self.user_stats['win_percentage']:.1f}%"
        stats_label = tk.Label(top_frame, text=stats_text, font=("Helvetica", 12), 
                              bg="#EBF5FB", fg=self.colors["dark"])
        stats_label.pack(pady=5)
        
        # Logout button (top right)
        logout_btn = tk.Button(
            top_frame, 
            text="Logout", 
            font=("Helvetica", 12), 
            command=self.logout,
            bg=self.colors["accent"], 
            fg="white",
            bd=0,
            padx=10,
            pady=3
        )
        logout_btn.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Game info display (hints used)
        info_frame = tk.Frame(main_container, bg="#EBF5FB")
        info_frame.pack(pady=5)
        self.hints_label = tk.Label(info_frame, text=f"Hints Used: {self.hints_used}/2", 
                                   font=("Helvetica", 14, "bold"), bg="#EBF5FB", fg=self.colors["info"])
        self.hints_label.pack()
        
        # Sudoku board grid with nicer styling
        self.entries = []
        board_frame = tk.Frame(main_container, bg=self.colors["cell_border"], bd=3, relief="solid")
        board_frame.pack(pady=15, padx=15)
        
        # Create the Sudoku grid with better cell styling
        for i in range(9):
            row_entries = []
            for j in range(9):
                # Add thicker borders for 3x3 box separation
                border_thickness = 1
                if i % 3 == 0 and i > 0:
                    border_thickness = 3
                if j % 3 == 0 and j > 0:
                    border_thickness = 3
                
                e = tk.Entry(board_frame, width=2, font=("Helvetica", 22, "bold"), justify="center", 
                           bd=border_thickness, relief="ridge")
                e.grid(row=i, column=j, padx=0, pady=0)
                
                # Set focus tracking for hint feature with visual feedback
                e.bind("<FocusIn>", lambda event, row=i, col=j: self.update_focus(row, col))
                
                # Populate the board
                if self.board[i][j] != 0:
                    e.insert(0, str(self.board[i][j]))
                    # Distinguish between original cells and user/hint filled cells
                    if self.original_board[i][j] != 0:
                        e.config(state="disabled", disabledforeground=self.colors["dark"], 
                                bg=self.colors["cell_original"])  # Gray background for original cells
                    else:
                        # Non-original filled cells (hints or user-entered)
                        e.config(bg=self.colors["cell_hint"])  # Light blue for hints
                else:
                    e.config(bg=self.colors["white"])  # White background for empty cells
                
                row_entries.append(e)
            self.entries.append(row_entries)
            
        # Buttons below the puzzle in a stylish container
        btn_container = tk.Frame(main_container, bg="#EBF5FB")
        btn_container.pack(pady=10)
        
        # Buttons below the puzzle (line 1)
        btn_frame1 = tk.Frame(btn_container, bg="#EBF5FB")
        btn_frame1.pack(pady=5)
        
        # Style buttons with more modern look
        tk.Button(btn_frame1, text="Hint", font=("Helvetica", 14), 
                command=self.hint, bg=self.colors["primary"], fg="white", 
                width=8, bd=0, padx=10, pady=5).grid(row=0, column=0, padx=5)
                
        tk.Button(btn_frame1, text="Solve", font=("Helvetica", 14), 
                command=self.solve_board, bg=self.colors["secondary"], fg="white", 
                width=8, bd=0, padx=10, pady=5).grid(row=0, column=1, padx=5)
                
        tk.Button(btn_frame1, text="Check Solution", font=("Helvetica", 14), 
                command=self.check_solution, bg=self.colors["info"], fg="white", 
                width=14, bd=0, padx=10, pady=5).grid(row=0, column=2, padx=5)
        
        # Buttons below the puzzle (line 2)
        btn_frame2 = tk.Frame(btn_container, bg="#EBF5FB")
        btn_frame2.pack(pady=5)
        
        tk.Button(btn_frame2, text="Reset", font=("Helvetica", 14), 
                command=self.reset_board, bg=self.colors["warning"], fg="white", 
                width=10, bd=0, padx=10, pady=5).grid(row=0, column=0, padx=5)
                
        tk.Button(btn_frame2, text="New Game", font=("Helvetica", 14), 
                command=lambda: self.show_difficulty_selection(True), bg=self.colors["secondary"], fg="white", 
                width=10, bd=0, padx=10, pady=5).grid(row=0, column=1, padx=5)
        
        # Buttons below the puzzle (line 3)
        btn_frame3 = tk.Frame(btn_container, bg="#EBF5FB")
        btn_frame3.pack(pady=5)
        
        tk.Button(btn_frame3, text="Leaderboard", font=("Helvetica", 14), 
                command=self.show_leaderboard, bg=self.colors["accent"], fg="white", 
                width=14, bd=0, padx=10, pady=5).pack()
        
        # Ensure game state is saved when closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_focus(self, row, col):
        """Track the currently focused cell for targeted hints and provide visual feedback"""
        # Reset background of previously focused cell if it exists
        if self.current_focus:
            prev_row, prev_col = self.current_focus
            # Only update if it's not a fixed cell
            if self.original_board[prev_row][prev_col] == 0:
                # Restore appropriate background based on content
                entry_value = self.entries[prev_row][prev_col].get()
                if entry_value:
                    self.entries[prev_row][prev_col].config(bg=self.colors["cell_user"])
                else:
                    self.entries[prev_row][prev_col].config(bg=self.colors["white"])
        
        # Update current focus
        self.current_focus = (row, col)
        
        # Highlight new focused cell if it's not a fixed cell
        if self.original_board[row][col] == 0:
            self.entries[row][col].config(bg=self.colors["cell_selected"])
            
    def generate_playable_board(self, difficulty="medium"):
        """Generate a board with a guaranteed single solution"""
        # We'll use the improved generate_board function from sudoku_logic
        # The improved function already ensures a valid board with a single solution
        
        # Generate board using the improved function in sudoku_logic.py
        board = None
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                board = generate_board(difficulty=difficulty)
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
        # Delete current game from the backend
        try:
            if self.user_id:
                requests.delete(f"{API_URL}/delete_game/{self.user_id}")
        except Exception:
            pass  # Ignore errors here
        
        # Stop the current timer if running
        self.stop_timer()
        
        # Generate a new board and refresh the UI
        if hasattr(self, 'selected_difficulty'):
            self.board = self.generate_playable_board(self.selected_difficulty)
        else:
            self.board = self.generate_playable_board("medium")  # Default to medium if no selection
        
        self.original_board = [[cell for cell in row] for row in self.board]
        self.hints_used = 0
        self.solved_by_algorithm = False
        self.time_remaining = 30 * 60  # Reset timer to 30 minutes
        self.time_expired = False
    
        # Save the new game with is_new_game flag set to True to increment the counter
        try:
            requests.post(f"{API_URL}/save_game", json={
                "user_id": self.user_id,
                "board_state": json.dumps(self.board),
                "original_board": json.dumps(self.original_board),
                "completed": False,
                "hints_used": 0,
                "solved_by_algorithm": False,
                "time_remaining": self.time_remaining,
                "time_expired": self.time_expired,
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
                        "solved_by_algorithm": data.get("solved_by_algorithm", False),
                        "time_remaining": data.get("time_remaining", 30 * 60),
                        "time_expired": data.get("time_expired", False)
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
                "solved_by_algorithm": self.solved_by_algorithm,
                "time_remaining": self.time_remaining,
                "time_expired": self.time_expired
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
        
        # Create a clean copy of the original board for solving
        solution_board = copy.deepcopy(self.original_board)
        if solve(solution_board):
            # If a cell is focused, provide hint for that specific cell
            if self.current_focus:
                row, col = self.current_focus
                # Provide hint regardless of current value (correct or incorrect)
                correct_val = solution_board[row][col]
                self.entries[row][col].delete(0, tk.END)
                self.entries[row][col].insert(0, str(correct_val))
                self.entries[row][col].config(bg="#D4E6F1")  # Light blue background for hints
                self.save_game()
                return
            
            # If no cell is focused, find first empty cell
            for i in range(9):
                for j in range(9):
                    # Check if cell is empty or has an incorrect value
                    entry_value = self.entries[i][j].get()
                    try:
                        current_val = int(entry_value) if entry_value else 0
                    except ValueError:
                        current_val = 0
                    
                    if current_val != solution_board[i][j]:
                        correct_val = solution_board[i][j]
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(correct_val))
                        self.entries[i][j].config(bg="#D4E6F1")  # Light blue background for hints
                        self.save_game()
                        return
                        
            messagebox.showinfo("Hint", "No incorrect or empty cells available for a hint.")
            # Revert the hint counter
            self.hints_used -= 1
            self.hints_label.config(text=f"Hints Used: {self.hints_used}/2")
        else:
            # Revert the hint counter since we couldn't provide a hint
            self.hints_used -= 1
            self.hints_label.config(text=f"Hints Used: {self.hints_used}/2")
            messagebox.showerror("Error", "Unable to compute hint. Please try again.")

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
            # Determine if this counts as a valid win (≤2 hints, no solve button, and no time expired)
            valid_win = self.hints_used <= 2 and not self.solved_by_algorithm and not self.time_expired
            
            if valid_win:
                messagebox.showinfo("Correct", "Congratulations! Your solution is correct. This counts as a win!")
            else:
                reason = ""
                if self.hints_used > 2:
                    reason = "You used more than 2 hints."
                elif self.solved_by_algorithm:
                    reason = "You used the solve button."
                elif self.time_expired:
                    reason = "You exceeded the 30-minute time limit."
                
                messagebox.showinfo("Correct", f"Your solution is correct, but it doesn't count as a win because {reason}")
            
            # Stop the timer
            self.stop_timer()
            
            # Save the completed game with win status
            self.save_game(completed=True)
            
            # Ask if user wants to start a new game
            if messagebox.askyesno("New Game", "Would you like to start a new game?"):
                self.new_game()
        else:
            messagebox.showinfo("Incorrect", "Your solution contains errors. Please check and try again.")

    def solve_board(self):
        # Mark that the solve algorithm was used
        self.solved_by_algorithm = True
        
        # Create a solution based on the original board
        solution_board = copy.deepcopy(self.original_board)
        
        if solve(solution_board):
            # Update the board with the solution, replacing all user inputs
            for i in range(9):
                for j in range(9):
                    if self.original_board[i][j] == 0:  # Only update non-original cells
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(solution_board[i][j]))
                        self.entries[i][j].config(bg="#ABEBC6")  # Light green for solved cells
            
            self.save_game(completed=True)
            messagebox.showinfo("Solved", "Puzzle solved! Note that using the solve button means this won't count as a win.")
        else:
            messagebox.showerror("Error", "No solution exists for this puzzle. Please try a different puzzle.")

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
        self.stop_timer()  # Stop the timer when logging out
        self.user_id = None
        self.board = None
        self.create_login_screen()

    def on_close(self):
        self.save_game()
        self.stop_timer()  # Stop the timer when closing the app
        self.root.destroy()

    def format_time(self, seconds):
        """Format seconds into MM:SS format"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"Time: {minutes:02d}:{seconds:02d}"
        
    def start_timer(self):
        """Start or resume the timer countdown"""
        if not self.timer_running and self.time_remaining > 0:
            self.timer_running = True
            self.update_timer()
            
    def stop_timer(self):
        """Stop the timer"""
        self.timer_running = False
        
    def update_timer(self):
        """Update the timer display and check if time is up"""
        if self.timer_running and self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_label.config(text=self.format_time(self.time_remaining))
            
            # Change color to warning when less than 5 minutes remaining
            if self.time_remaining < 300 and self.time_remaining > 0:
                self.timer_label.config(fg=self.colors["warning"])
                
            # Check if time is up
            if self.time_remaining <= 0:
                self.time_expired = True
                self.time_remaining = 0
                self.timer_label.config(text=self.format_time(0), fg=self.colors["warning"])
                messagebox.showwarning("Time Expired", 
                                     "Time limit exceeded! You can continue playing, but no points will be awarded for completing this puzzle.")
                self.save_game()  # Save the time_expired status
            else:
                # Schedule the next update after 1 second
                self.root.after(1000, self.update_timer)

def run_frontend():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_frontend()