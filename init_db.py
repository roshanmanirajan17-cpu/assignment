<<<<<<< HEAD
from app import app
from models import db

with app.app_context():

    db.create_all()

    print("Database Created")
=======
import importlib.util
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src-election-system")
os.chdir(SRC_DIR)

sys.path.insert(0, SRC_DIR)
MODULE_PATH = os.path.join(SRC_DIR, "init_db.py")

spec = importlib.util.spec_from_file_location("assignment_init_db", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
>>>>>>> 30d33a7fad676b6f54f22ae14fd4bdd6a2557903
