from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask import flash

from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from werkzeug.security import check_password_hash

from config import Config
from models import *

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            if user.role == 'admin':
                return redirect('/admin')

            return redirect('/student')

        flash('Invalid Login')

    return render_template('login.html')


@app.route('/student')
@login_required
def student():

    if current_user.role != 'student':
        return redirect('/')

    candidates = Candidate.query.all()

    return render_template(
        'student_dashboard.html',
        candidates=candidates
    )


@app.route('/vote/<int:id>')
@login_required
def vote(id):

    if current_user.voted:
        flash('You have already voted')
        return redirect('/student')

    candidate = Candidate.query.get(id)

    candidate.votes += 1

    current_user.voted = True

    vote = Vote(
        voter_id=current_user.id,
        candidate_id=id
    )

    db.session.add(vote)

    db.session.commit()

    flash('Vote Submitted Successfully')

    return redirect('/student')


@app.route('/admin')
@login_required
def admin():

    if current_user.role != 'admin':
        return redirect('/')

    candidates = Candidate.query.order_by(
        Candidate.votes.desc()
    ).all()

    total_students = User.query.filter_by(
        role='student'
    ).count()

    votes_cast = User.query.filter_by(
        role='student',
        voted=True
    ).count()

    participation = 0

    if total_students > 0:
        participation = round(
            votes_cast / total_students * 100,
            2
        )

    return render_template(
        'admin_dashboard.html',
        candidates=candidates,
        total_students=total_students,
        votes_cast=votes_cast,
        participation=participation
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)