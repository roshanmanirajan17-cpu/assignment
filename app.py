<<<<<<< HEAD
from flask import Flask, render_template, request, redirect
from flask import url_for, flash, send_file, send_from_directory

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import os
import csv
import shutil

from config import Config
from models import *

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


def ensure_default_users():
    default_users = [
        ("admin", "12345", "admin"),
        ("student1", "123456", "student"),
        ("student2", "123456", "student"),
        ("student3", "123456", "student"),
    ]

    for username, password, role in default_users:
        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(
                username=username,
                password=generate_password_hash(password),
                role=role,
            )
            db.session.add(user)
        else:
            if user.role != role:
                user.role = role
            if not check_password_hash(user.password, password):
                user.password = generate_password_hash(password)

    db.session.commit()


with app.app_context():
    db.create_all()
    ensure_default_users()


def ensure_sample_results():
    if Position.query.count() > 0 or Candidate.query.count() > 0:
        return

    sample_positions = [
        (
            "President",
            [
                ("Alex Johnson", "Improve facilities and campus life.", "candidate1.jpg"),
                ("Chris Lee", "Student welfare and academic support.", "candidate2.jpg"),
                ("Maria Garcia", "Campus events and student engagement.", "candidate3.jpg"),
            ],
        ),
        (
            "Secretary",
            [
                ("Jackson Michel", "Strengthen student services.", "candidate4.jpg"),
                ("Tupac", "Enhance communication channels.", "candidate5.jpg"),
                ("Musk Elon", "Secure student resources.", "candidate6.jpg"),
            ],
        ),
        (
            "Treasurer",
            [
                ("Brad Hudson", "Budget transparency and support.", "candidate7.jpg"),
                ("Robert Olise", "Sustainable financial planning.", "candidate8.jpg"),
            ],
        ),
    ]

    for position_name, candidates in sample_positions:
        position = Position.query.filter_by(name=position_name).first()
        if not position:
            position = Position(name=position_name)
            db.session.add(position)
            db.session.flush()

        for candidate_name, manifesto, image in candidates:
            if not Candidate.query.filter_by(name=candidate_name, position_id=position.id).first():
                db.session.add(
                    Candidate(
                        name=candidate_name,
                        manifesto=manifesto,
                        image=image,
                        position_id=position.id,
                    )
                )

    db.session.commit()


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.environ.get(
    "UPLOAD_FOLDER",
    os.path.join(BASE_DIR, "instance", "uploads")
)
STATIC_UPLOADS_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if os.path.isdir(STATIC_UPLOADS_FOLDER):
    for filename in os.listdir(STATIC_UPLOADS_FOLDER):
        source_path = os.path.join(STATIC_UPLOADS_FOLDER, filename)
        destination_path = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.isfile(source_path) and not os.path.exists(destination_path):
            shutil.copy2(source_path, destination_path)

# --------------------------------
# Login Manager
# --------------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------------------
# UPLOADED FILES
# --------------------------------

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# --------------------------------
# LOGIN
# --------------------------------

@app.route("/", methods=["GET", "POST"])
def login():

    with app.app_context():
        db.create_all()
        ensure_default_users()

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("student_dashboard"))

        flash("Invalid Username or Password")

    return render_template("login.html")


# --------------------------------
# LOGOUT
# --------------------------------

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully")

    return redirect("/")


# --------------------------------
# STUDENT DASHBOARD
# --------------------------------

@app.route("/student")
@login_required
def student_dashboard():

    if current_user.role != "student":
        return redirect("/")

    positions = Position.query.all()

    return render_template(
        "student_dashbaord.html",
        positions=positions
    )


# --------------------------------
# VOTING
# --------------------------------

@app.route("/vote/<int:position_id>/<int:candidate_id>")
@login_required
def vote(position_id, candidate_id):

    if current_user.role != "student":
        return redirect("/")

    existing_vote = Vote.query.filter_by(
        voter_id=current_user.id,
        position_id=position_id
    ).first()

    if existing_vote:

        flash("You already voted for this position.")

        return redirect(url_for(
            "student_dashboard"
        ))

    candidate = Candidate.query.get_or_404(
        candidate_id
    )

    candidate.votes += 1

    vote_record = Vote(
        voter_id=current_user.id,
        candidate_id=candidate.id,
        position_id=position_id
    )

    db.session.add(vote_record)

    db.session.commit()

    flash(
        f"Vote submitted for {candidate.name}"
    )

    return redirect(
        url_for("student_dashboard")
    )


# --------------------------------
# ADMIN DASHBOARD
# --------------------------------

@app.route("/admin")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return redirect("/")

    positions = Position.query.all()

    candidates = Candidate.query.order_by(
        Candidate.votes.desc()
    ).all()

    total_students = User.query.filter_by(
        role="student"
    ).count()

    total_participants = Candidate.query.count()

    voters = Vote.query.with_entities(
        Vote.voter_id
    ).distinct().count()

    participation = 0

    if total_students > 0:
        participation = round(
            voters / total_students * 100,
            2
        )

    # Get leading candidate: must have votes > 0 and be sole leader (no ties)
    leading_candidate = None
    top_candidate = Candidate.query.filter(
        Candidate.votes > 0
    ).order_by(
        Candidate.votes.desc()
    ).first()

    if top_candidate:
        # Check if there's a tie for highest votes
        max_votes = top_candidate.votes
        tied_candidates = Candidate.query.filter(
            Candidate.votes == max_votes
        ).count()

        # Only set as leader if no tie (only one candidate with max votes)
        if tied_candidates == 1:
            leading_candidate = top_candidate

    return render_template(
        "admin_dashboard.html",
        positions=positions,
        candidates=candidates,
        total_students=total_students,
        total_participants=total_participants,
        voters=voters,
        participation=participation,
        leader=leading_candidate
    )


# --------------------------------
# ADD CANDIDATE
# --------------------------------

@app.route("/candidate/add",
           methods=["GET", "POST"])
@login_required
def add_candidate():

    if current_user.role != "admin":
        return redirect("/")

    positions = Position.query.all()

    if request.method == "POST":

        name = request.form["name"]

        manifesto = request.form["manifesto"]

        position_id = request.form["position"]

        image = request.files["image"]

        filename = ""

        if image:

            filename = secure_filename(
                image.filename
            )

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        candidate = Candidate(
            name=name,
            manifesto=manifesto,
            image=filename,
            position_id=position_id
        )

        db.session.add(candidate)

        db.session.commit()

        flash("Candidate Added")

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "add_candidate.html",
        positions=positions
    )


# --------------------------------
# EDIT CANDIDATE
# --------------------------------

@app.route("/candidate/edit/<int:id>",
           methods=["GET", "POST"])
@login_required
def edit_candidate(id):

    if current_user.role != "admin":
        return redirect("/")

    candidate = Candidate.query.get_or_404(
        id
    )

    positions = Position.query.all()

    if request.method == "POST":

        candidate.name = request.form["name"]

        candidate.manifesto = request.form[
            "manifesto"
        ]

        candidate.position_id = request.form[
            "position"
        ]

        image = request.files["image"]

        if image and image.filename:

            filename = secure_filename(
                image.filename
            )

            image.save(
                os.path.join(
                    app.config[
                        "UPLOAD_FOLDER"
                    ],
                    filename
                )
            )

            candidate.image = filename

        db.session.commit()

        flash("Candidate Updated")

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "edit_candidate.html",
        candidate=candidate,
        positions=positions
    )


# --------------------------------
# DELETE CANDIDATE
# --------------------------------

@app.route("/candidate/delete/<int:id>")
@login_required
def delete_candidate(id):

    if current_user.role != "admin":
        return redirect("/")

    candidate = Candidate.query.get_or_404(
        id
    )

    db.session.delete(candidate)

    db.session.commit()

    flash("Candidate Deleted")

    return redirect(
        url_for("admin_dashboard")
    )


# --------------------------------
# LIVE RESULTS PAGE
# --------------------------------

@app.route("/results")
def results():

    ensure_sample_results()

    positions = Position.query.order_by(Position.id).all()

    return render_template(
        "results.html",
        positions=positions
    )


# --------------------------------
# EXPORT CSV
# --------------------------------

@app.route("/export")
@login_required
def export_results():

    if current_user.role != "admin":
        return redirect("/")

    file_path = "results.csv"

    with open(
        file_path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Candidate",
            "Position",
            "Votes"
        ])

        candidates = Candidate.query.all()

        for c in candidates:

            writer.writerow([
                c.name,
                c.position.name,
                c.votes
            ])

    return send_file(
        file_path,
        as_attachment=True
    )


# --------------------------------
# CREATE DB
# --------------------------------

@app.cli.command("create-db")
def create_db():

    db.create_all()

    print("Database Created")


# --------------------------------
# RUN
# --------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        debug=True,
        host="0.0.0.0",
        port=port
    )
=======
import importlib.util
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src-election-system")
os.chdir(SRC_DIR)

sys.path.insert(0, SRC_DIR)
MODULE_PATH = os.path.join(SRC_DIR, "app.py")

spec = importlib.util.spec_from_file_location("assignment_app", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

if hasattr(module, "app"):
    port = int(os.environ.get("PORT", 5000))
    module.app.run(debug=True, host="0.0.0.0", port=port)
else:
    raise RuntimeError("Failed to load Flask app from src-election-system/app.py")
>>>>>>> 30d33a7fad676b6f54f22ae14fd4bdd6a2557903
