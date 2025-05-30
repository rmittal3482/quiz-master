from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Subject, Chapter, Quiz, Question, Score
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

ADMIN_EMAIL = "admin@quizmaster.com"
ADMIN_PASSWORD = "admin123"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

    # Create admin user if not exists
    admin = User.query.filter_by(email=ADMIN_EMAIL).first()
    if not admin:
        admin_user = User(
            email=ADMIN_EMAIL,
            password=generate_password_hash(ADMIN_PASSWORD),
            full_name="Admin",
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            full_name=form.full_name.data,
            qualification=form.qualification.data,
            dob=form.dob.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            session['is_admin'] = user.is_admin
            return redirect(url_for('admin_dashboard' if user.is_admin else 'user_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

# Admin Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))

    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()
    users = User.query.filter_by(is_admin=False).all()  
    scores = Score.query.all()

    # 📊 Prepare chart data (Subjects vs Number of Quizzes)
    chart_labels = []
    chart_data = []

    for subject in subjects:
        quiz_count = 0
        for chapter in subject.chapters:
            quiz_count += len(chapter.quizzes)
        chart_labels.append(subject.name)
        chart_data.append(quiz_count)

    # 🏆 Prepare leaderboard data (Top 5 Users)
   # 🏆 Leaderboard with total score, total quizzes attempted, and average score
    leaderboard = (
        db.session.query(
            User,
            db.func.sum(Score.score).label('total_score'),
            db.func.count(Score.id).label('quizzes_attempted'),
            (db.func.avg(Score.score)).label('average_score')
        )
        .join(Score, User.id == Score.user_id)
        .group_by(User.id)
        .order_by(db.desc('total_score'))
        .limit(5)
        .all()
    )

    return render_template('admin_dashboard.html',
                           subjects=subjects,
                           chapters=chapters,
                           quizzes=quizzes,
                           users=users,
                           scores=scores,
                           chart_labels=chart_labels,
                           chart_data=chart_data,
                           leaderboard=leaderboard)   # ✅ Add leaderboard here

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))

    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)

    return render_template('admin_users.html', users=users)

@app.route('/admin/leaderboard')
@login_required
def admin_leaderboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))

    # Fetch users and their total scores
    leaderboard_data = (
        db.session.query(User, db.func.sum(Score.score))
        .join(Score)
        .filter(User.is_admin == False)
        .group_by(User.id)
        .order_by(db.func.sum(Score.score).desc())
        .all()
    )

    return render_template('admin_leaderboard.html', leaderboard=leaderboard_data)

@app.route('/admin/create_subject', methods=['GET', 'POST'])
@login_required
def create_subject():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        subject = Subject(name=name, description=desc)
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('create_subject.html')

@app.route('/admin/create_chapter/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def create_chapter(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))

    # Fetch the subject based on ID
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        chapter = Chapter(name=name, description=desc, subject_id=subject.id)
        db.session.add(chapter)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    # PASS the subject to the template
    return render_template('create_chapter.html', subject=subject)

@app.route('/admin/create_quiz/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def create_quiz(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))

    # Fetch the Chapter based on ID
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        quiz = Quiz(
            chapter_id=chapter.id,
            date_of_quiz=datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d'),
            time_duration=request.form['time_duration'],
            remarks=request.form['remarks']
        )
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    # PASS the chapter to the template
    return render_template('create_quiz.html', chapter=chapter)


@app.route('/admin/add_question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    if request.method == 'POST':
        question = Question(
            quiz_id=quiz_id,
            question_statement=request.form['question_statement'],
            option1=request.form['option1'],
            option2=request.form['option2'],
            option3=request.form['option3'],
            option4=request.form['option4'],
            correct_option=request.form['correct_option']
        )
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_question.html')

# User Routes
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    subjects = Subject.query.all()
    return render_template('user_dashboard.html', subjects=subjects)

@app.route('/user/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        total_score = 0

        for q in questions:
            user_answer = request.form.get(str(q.id))  # 🔥 Get user's selected option
            
            if user_answer == q.correct_option:        # 🔥 Match user's answer to correct answer
                total_score += 1                       # 🔥 Add 1 mark if correct

        score = Score(
            quiz_id=quiz_id,
            user_id=current_user.id,
            score=total_score,
            attempt_date=datetime.now()
        )
        db.session.add(score)
        db.session.commit()

        flash(f'Quiz submitted! You scored {total_score} out of {len(questions)}.', 'success')
        return redirect(url_for('view_scores'))

    return render_template('attempt_quiz.html', quiz=quiz, questions=questions)


@app.route('/user/view_scores')
@login_required
def view_scores():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    scores = Score.query.filter_by(user_id=current_user.id).all()
    return render_template('view_scores.html', scores=scores)

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
