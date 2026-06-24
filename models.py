from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True)

    password = db.Column(db.String(200))

    role = db.Column(db.String(20))

    voted = db.Column(db.Boolean, default=False)


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    manifesto = db.Column(db.Text)

    image = db.Column(db.String(200))

    position_id = db.Column(
        db.Integer,
        db.ForeignKey('position.id')
    )

    votes = db.Column(db.Integer, default=0)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    voter_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidate.id')
    )