# backend.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Game
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sudoku.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
        return jsonify({"message": "Login successful", "user_id": user.id}), 200
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
        if game:
            game.board_state = data['board_state']
            game.completed = data.get('completed', False)
        else:
            game = Game(user_id=data['user_id'], board_state=data['board_state'], completed=data.get('completed', False))
            db.session.add(game)
        
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
            return jsonify({"board_state": game.board_state}), 200
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
