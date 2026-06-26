from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    votes = db.relationship(
        "Vote",
        backref="voter",
        lazy=True
    )


class Position(db.Model):

    __tablename__ = "positions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    candidates = db.relationship(
        "Candidate",
        backref="position",
        lazy=True
    )


class Candidate(db.Model):

    __tablename__ = "candidates"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    manifesto = db.Column(
        db.Text,
        nullable=False
    )

    image = db.Column(
        db.String(255)
    )

    votes = db.Column(
        db.Integer,
        default=0
    )

    position_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "positions.id"
        )
    )


class Vote(db.Model):

    __tablename__ = "votes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    voter_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        )
    )

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "candidates.id"
        )
    )

    position_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "positions.id"
        )
    )