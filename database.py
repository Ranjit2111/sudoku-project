# database.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    games = db.relationship('Game', backref='user', lazy=True, cascade="all, delete-orphan")
    
    # User statistics
    puzzles_played = db.Column(db.Integer, default=0)
    puzzles_solved = db.Column(db.Integer, default=0)
    win_percentage = db.Column(db.Float, default=0.0)

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    board_state = db.Column(db.Text, nullable=False)  # Stores board as JSON string
    original_board = db.Column(db.Text, nullable=False)  # Stores original board state
    completed = db.Column(db.Boolean, default=False)
    hints_used = db.Column(db.Integer, default=0)  # Track hints used
    solved_by_algorithm = db.Column(db.Boolean, default=False)  # Track if solved button was used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)