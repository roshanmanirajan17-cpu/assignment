from werkzeug.security import generate_password_hash

from app import app
from models import *

with app.app_context():

    admin = User(
        username='admin',
        password=generate_password_hash('admin123'),
        role='admin'
    )

    student1 = User(
        username='student1',
        password=generate_password_hash('123456'),
        role='student'
    )

    student2 = User(
        username='student2',
        password=generate_password_hash('123456'),
        role='student'
    )

    president = Position(name='President')

    db.session.add(president)

    db.session.commit()

    c1 = Candidate(
        name='Alex Johnson',
        manifesto='Improve campus facilities',
        image='candidate1.jpg',
        position_id=president.id
    )

    c2 = Candidate(
        name='Chris Lee',
        manifesto='Enhance student welfare',
        image='candidate2.jpg',
        position_id=president.id
    )

    c3 = Candidate(
        name='Maria Garcia',
        manifesto='More events and opportunities',
        image='candidate3.jpg',
        position_id=president.id
    )

    db.session.add_all([
        admin,
        student1,
        student2,
        c1,
        c2,
        c3
    ])

    db.session.commit()

print("Sample Data Inserted")