from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from datetime import datetime


db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    toddlers = db.relationship('Toddler', backref='parent', lazy=True)

class Toddler(db.Model):
    __tablename__ = 'toddlers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True, default="https://media.istockphoto.com/id/1358260836/vector/toddler-sitting.jpg?s=612x612&w=0&k=20&c=Yo6Ct1RLLBdsdYM5eoyWOz8GY-2-7kuGn-6MWoSP68Y=") 
    learned_words = db.relationship('ToddlerWord', backref='toddler', lazy=True)

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    definition = db.Column(db.String(255), nullable=True)
    learned_by = db.relationship('ToddlerWord', backref='word', lazy=True)
    art = db.relationship('WordArt', backref='word', uselist=False)
    
class SuggestedWord(db.Model):
    __tablename__ = 'suggested_words'
    id = db.Column(db.Integer, primary_key=True)
    toddler_id = db.Column(db.Integer, db.ForeignKey('toddlers.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    suggested_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_learned = db.Column(db.Boolean, default=False, nullable=False)


class ToddlerWord(db.Model):
    __tablename__ = 'toddler_words'
    id = db.Column(db.Integer, primary_key=True)
    toddler_id = db.Column(db.Integer, db.ForeignKey('toddlers.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)

class WordArt(db.Model):
    __tablename__ = 'word_arts'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    art_image_url = db.Column(db.String(255), nullable=False)


def connect_db(app):
    db.app = app
    db.init_app(app)

