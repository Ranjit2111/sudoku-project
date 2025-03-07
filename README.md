# Sudoku Game Application

A full-featured Sudoku game with a modern UI, user authentication, game saving, and leaderboard functionality.

![Sudoku Game](https://github.com/Ranjit2111/sudoku-project/raw/main/screenshots/game_screen.png)

## Features

- **User Authentication**: Register and login to track your progress
- **Multiple Difficulty Levels**: Easy, Medium, and Hard puzzles
- **Game Saving**: Continue your game where you left off
- **Hint System**: Get up to 2 hints per game without affecting your win status
- **Leaderboard**: Compete with other players
- **Solve Button**: Automatically solve the current puzzle (won't count as a win)
- **Statistics Tracking**: Track your games played, games won, and win percentage

## Architecture

The application follows a client-server architecture:

- **Frontend**: Tkinter-based GUI for game interaction
- **Backend**: Flask REST API for user management and game state persistence
- **Database**: SQLite database for storing user data and game states

## Installation

### Prerequisites

- Python 3.7 or higher
- Git

### Clone the Repository

```bash
git clone https://github.com/Ranjit2111/sudoku-project.git
cd sudoku-project
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode

Run the application in development mode:

```bash
python app.py
```

This will start both the backend server and the frontend application.

### Building an Executable

To build a standalone executable:

```bash
python build.py
```

This will create an executable in the `dist` folder that can be run without Python installed.

## How to Play

1. **Register/Login**: Create an account or login to an existing one
2. **Start a New Game**: Select a difficulty level (Easy, Medium, Hard)
3. **Game Rules**:
   - Fill in the grid so that every row, column, and 3×3 box contains the digits 1-9
   - Use up to 2 hints without affecting your win status
   - Complete the puzzle correctly to win
4. **Continue a Game**: Resume a previously saved game
5. **Check Solution**: Verify if your solution is correct
6. **View Leaderboard**: See how you rank against other players

## Game Controls

- **Left-click**: Select a cell
- **Number keys**: Enter a number in the selected cell
- **Hint Button**: Get a hint for a difficult cell
- **Solve Button**: Automatically solve the puzzle (won't count as a win)
- **Check Solution Button**: Verify if your solution is correct
- **Reset Button**: Reset the board to its initial state
- **New Game Button**: Start a new game
- **Leaderboard Button**: View the leaderboard

## Technical Details

### Frontend (frontend.py)

The frontend is built with Tkinter and provides:
- User interface for game interaction
- Board rendering and input handling
- Game state visualization

### Backend (backend.py)

The backend is a Flask REST API that provides:
- User authentication and registration
- Game state persistence
- Leaderboard functionality

### Database (database.py)

The SQLite database stores:
- User accounts and credentials
- Game states and progress
- User statistics

### Sudoku Logic (sudoku_logic.py)

Contains the core game logic:
- Board generation with varying difficulty levels
- Solution validation
- Hint generation
- Board solving algorithms

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped with the development
- Special thanks to the open-source community for providing valuable resources

## Contact

Project Link: [https://github.com/Ranjit2111/sudoku-project](https://github.com/Ranjit2111/sudoku-project) 