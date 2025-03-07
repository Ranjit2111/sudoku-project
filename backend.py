# backend.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Game
import json
import os
import sys

app = Flask(__name__)

# Get the base directory of the application
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (compiled with PyInstaller)
    basedir = os.path.dirname(sys.executable)
else:
    # If the application is run from script
    basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "sudoku.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400
    # Use pbkdf2 with sha256 for better security
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({
            "message": "Login successful", 
            "user_id": user.id,
            "stats": {
                "puzzles_played": user.puzzles_played,
                "puzzles_solved": user.puzzles_solved,
                "win_percentage": user.win_percentage
            }
        }), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/save_game', methods=['POST'])
def save_game():
    data = request.get_json()
    if not data or 'user_id' not in data or 'board_state' not in data:
        return jsonify({"message": "Missing data"}), 400
    
    try:
        # Parse board_state to ensure it's valid JSON
        json.loads(data['board_state'])
        
        # Look for an existing unfinished game for this user
        game = Game.query.filter_by(user_id=data['user_id'], completed=False).first()
        
        # Check if this is a new game creation 
        is_new_game = False
        if not game:
            is_new_game = True
            
        if game:
            # Update existing game
            game.board_state = data['board_state']
            was_completed = game.completed
            game.completed = data.get('completed', False)
            
            # Update hints and solved status
            if 'hints_used' in data:
                game.hints_used = data['hints_used']
            if 'solved_by_algorithm' in data:
                game.solved_by_algorithm = data['solved_by_algorithm']
                
            # If game is completed, update user statistics
            if data.get('completed', False) and not was_completed:
                user = User.query.get(data['user_id'])
                user.puzzles_played += 1
                
                # Count as solved only if user didn't use too many hints or the solve button
                if game.hints_used <= 2 and not game.solved_by_algorithm:
                    user.puzzles_solved += 1
                
                # Update win percentage
                if user.puzzles_played > 0:
                    user.win_percentage = (user.puzzles_solved / user.puzzles_played) * 100
        else:
            # Create new game with original board state
            game = Game(
                user_id=data['user_id'], 
                board_state=data['board_state'],
                original_board=data.get('original_board', data['board_state']),
                completed=data.get('completed', False),
                hints_used=data.get('hints_used', 0),
                solved_by_algorithm=data.get('solved_by_algorithm', False)
            )
            db.session.add(game)
            
            # If this is a new game creation after explicitly starting a new game
            # (not just loading the app for the first time)
            if data.get('is_new_game', False):
                user = User.query.get(data['user_id'])
                # Increment games_played if the previous game was abandoned
                previous_completed_game = Game.query.filter_by(
                    user_id=data['user_id'], 
                    completed=True
                ).order_by(Game.updated_at.desc()).first()
                
                # If there's no previous completed game or the last game was explicitly marked as completed
                if not previous_completed_game:
                    user.puzzles_played += 1
                    if user.puzzles_played > 0:
                        user.win_percentage = (user.puzzles_solved / user.puzzles_played) * 100
        
        db.session.commit()
        return jsonify({"message": "Game saved successfully"}), 200
    except json.JSONDecodeError:
        return jsonify({"message": "Invalid board state format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error saving game: {str(e)}"}), 500

@app.route('/load_game/<int:user_id>', methods=['GET'])
def load_game(user_id):
    try:
        game = Game.query.filter_by(user_id=user_id, completed=False).first()
        if game:
            # Verify the JSON is valid
            board = json.loads(game.board_state)
            original = json.loads(game.original_board)
            return jsonify({
                "board_state": game.board_state,
                "original_board": game.original_board,
                "hints_used": game.hints_used,
                "solved_by_algorithm": game.solved_by_algorithm
            }), 200
        else:
            return jsonify({"message": "No saved game found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error loading game: {str(e)}"}), 500

@app.route('/delete_game/<int:user_id>', methods=['DELETE'])
def delete_game(user_id):
    try:
        game = Game.query.filter_by(user_id=user_id, completed=False).first()
        if game:
            db.session.delete(game)
            db.session.commit()
            return jsonify({"message": "Game deleted"}), 200
        return jsonify({"message": "No game to delete"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting game: {str(e)}"}), 500

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        # Get all users (not just those who have played games)
        users = User.query.order_by(User.win_percentage.desc(), User.puzzles_solved.desc()).all()
        
        leaderboard = []
        for user in users:
            leaderboard.append({
                "username": user.username,
                "puzzles_played": user.puzzles_played,
                "puzzles_solved": user.puzzles_solved,
                "win_percentage": round(user.win_percentage, 2)
            })
            
        return jsonify({"leaderboard": leaderboard}), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching leaderboard: {str(e)}"}), 500

def run_backend():
    try:
        with app.app_context():
            db.create_all()
        # Run on port 5000 and bind to localhost
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f"Error starting backend server: {e}")
        return

if __name__ == '__main__':
    run_backend()