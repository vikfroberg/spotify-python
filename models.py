from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)


class Search(db.Model):
    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key = True)
    q = db.Column(db.String(120), unique=True, nullable=False)
    type = db.Column(db.String(120), nullable=False)
    playlist_id = db.Column(db.Integer)
