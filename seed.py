<<<<<<< HEAD
from app import app, ensure_default_users
from models import *


def get_or_create_user(username, password, role):
    user = User.query.filter_by(username=username).first()
    if user:
        return user
    user = User(username=username, password=generate_password_hash(password), role=role)
    db.session.add(user)
    return user


def get_or_create_position(name):
    position = Position.query.filter_by(name=name).first()
    if position:
        return position
    position = Position(name=name)
    db.session.add(position)
    return position


def get_or_create_candidate(name, manifesto, image, position):
    candidate = Candidate.query.filter_by(name=name, position_id=position.id).first()
    if candidate:
        if candidate.image != image or candidate.manifesto != manifesto:
            candidate.image = image
            candidate.manifesto = manifesto
        return candidate
    candidate = Candidate(name=name, manifesto=manifesto, image=image, position_id=position.id)
    db.session.add(candidate)
    return candidate

with app.app_context():
    db.create_all()
    ensure_default_users()

    admin = get_or_create_user("admin", "12345", "admin")
    s1 = get_or_create_user("student1", "123456", "student")
    s2 = get_or_create_user("student2", "123456", "student")
    s3 = get_or_create_user("student3", "123456", "student")

    president = get_or_create_position("President")
    secretary = get_or_create_position("Secretary")
    treasurer = get_or_create_position("Treasurer")

    db.session.flush()

    get_or_create_candidate("Alex Johnson", "Improve facilities and campus life.", "candidate1.jpg", president)
    get_or_create_candidate("Chris Lee", "Student welfare and academic support.", "candidate2.jpg", president)
    get_or_create_candidate("Maria Garcia", "Campus events and student engagement.", "candidate3.jpg", president)
    get_or_create_candidate("Jackson Michel", "Strengthen student services.", "candidate4.jpg", secretary)
    get_or_create_candidate("Tupac", "Enhance communication channels.", "candidate5.jpg", secretary)
    get_or_create_candidate("Musk Elon", "Secure student resources.", "candidate6.jpg", secretary)
    get_or_create_candidate("Brad Hudson", "Budget transparency and support.", "candidate7.jpg", treasurer)
    get_or_create_candidate("Robert Olise", "Sustainable financial planning.", "candidate8.jpg", treasurer)

    db.session.commit()
    print("Sample Data Inserted or already present")
=======
import importlib.util
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src-election-system")
os.chdir(SRC_DIR)

sys.path.insert(0, SRC_DIR)
MODULE_PATH = os.path.join(SRC_DIR, "seed.py")

spec = importlib.util.spec_from_file_location("assignment_seed", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
>>>>>>> 30d33a7fad676b6f54f22ae14fd4bdd6a2557903
