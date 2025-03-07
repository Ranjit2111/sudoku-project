# frontend.py
import tkinter as tk
from tkinter import messagebox
import requests
import json
import sys
from sudoku_logic import generate_board, solve, board_to_string, string_to_board, is_valid_board

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
        # Attempt to load a saved game; if none, generate a new one.
        loaded_game = self.load_saved_game()
        if loaded_game:
            self.board = loaded_game
            self.original_board = [[cell if cell != 0 else 0 for cell in row] for row in self.board]
        else:
            self.board = generate_board()
            self.original_board = [[cell if cell != 0 else 0 for cell in row] for row in self.board]
        
        self.entries = []
        board_frame = tk.Frame(self.root)
        board_frame.pack(pady=20)
        
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
                
                if self.board[i][j] != 0:
                    e.insert(0, str(self.board[i][j]))
                    e.config(state="disabled", disabledforeground="black")
                row_entries.append(e)
            self.entries.append(row_entries)
            
        # Buttons for game options
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Hint", font=("Helvetica", 16), command=self.hint, bg="#3498DB", fg="white", width=10).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="New Game", font=("Helvetica", 16), command=self.new_game, bg="#2ECC71", fg="white", width=10).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Solve", font=("Helvetica", 16), command=self.solve_board, bg="#1ABC9C", fg="white", width=10).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Logout", font=("Helvetica", 16), command=self.logout, bg="#7D3C98", fg="white", width=10).grid(row=0, column=3, padx=5)
        
        # Check solution button
        tk.Button(self.root, text="Check Solution", font=("Helvetica", 16), command=self.check_solution, bg="#F39C12", fg="white", width=15).pack(pady=10)
        
        # Ensure game state is saved when closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

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
            self.board = generate_board()
            self.original_board = [[cell if cell != 0 else 0 for cell in row] for row in self.board]
            self.create_game_screen()

    def load_saved_game(self):
        try:
            response = requests.get(f"{API_URL}/load_game/{self.user_id}")
            if response.status_code == 200:
                data = response.json()
                board_state = data.get("board_state")
                if board_state:
                    return json.loads(board_state)
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
                "completed": completed
            })
            
            if response.status_code != 200:
                messagebox.showerror("Error", f"Failed to save game: {response.json().get('message', 'Unknown error')}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not save game. {e}")

    def hint(self):
        # Provide one hint by finding the first empty cell and inserting the correct number from solution.
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
            
        solution_board = [row[:] for row in current_board]
        if solve(solution_board):
            for i in range(9):
                for j in range(9):
                    if current_board[i][j] == 0:
                        correct_val = solution_board[i][j]
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(correct_val))
                        self.entries[i][j].config(bg="#D4E6F1")  # Light blue background for hints
                        self.board[i][j] = correct_val
                        self.save_game()
                        return
            messagebox.showinfo("Hint", "No empty cells available for a hint.")
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
            messagebox.showinfo("Correct", "Congratulations! Your solution is correct.")
            self.save_game(completed=True)
        else:
            messagebox.showinfo("Incorrect", "Your solution contains errors. Please check and try again.")

    def solve_board(self):
        # Solve and display the complete solution
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
            
        if solve(current_board):
            for i in range(9):
                for j in range(9):
                    if self.original_board[i][j] == 0:  # Only update non-original cells
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(current_board[i][j]))
                        self.entries[i][j].config(bg="#ABEBC6")  # Light green for solved cells
            self.save_game(completed=True)
            messagebox.showinfo("Solved", "Puzzle solved!")
        else:
            messagebox.showerror("Error", "No solution exists for the current board.")

    def give_up(self):
        # Reveal the full solution, then ask if the user wants to retry or start a new game.
        current_board = []
        for i in range(9):
            row = []
            for j in range(9):
                try:
                    val = int(self.entries[i][j].get())
                except ValueError:
                    val = 0
                row.append(val)
            current_board.append(row)
        if solve(current_board):
            for i in range(9):
                for j in range(9):
                    self.entries[i][j].delete(0, tk.END)
                    self.entries[i][j].insert(0, str(current_board[i][j]))
                    self.entries[i][j].config(state="disabled", disabledforeground="red")
            self.save_game(completed=True)
            if messagebox.askyesno("Give Up", "Puzzle solved. Would you like to retry the same puzzle?"):
                self.create_game_screen()
            else:
                self.create_game_screen()
        else:
            messagebox.showerror("Error", "No solution exists for the current board.")

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
