from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

# Setup Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300))

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Integer)
    remarks = db.Column(db.String(300))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.String(300), nullable=False)
    option1 = db.Column(db.String(100))
    option2 = db.Column(db.String(100))
    option3 = db.Column(db.String(100))
    option4 = db.Column(db.String(100))
    correct_option = db.Column(db.String(100))

# Generate Database
with app.app_context():
    db.drop_all()
    db.create_all()

    # Create Admin User
    admin_user = User(
        email="admin@example.com",
        password=generate_password_hash("admin123"),
        full_name="Admin",
        is_admin=True
    )
    db.session.add(admin_user)

    # Create Subjects
    math = Subject(name="Mathematics", description="Learn numbers and formulas.")
    science = Subject(name="Science", description="Explore the natural world.")
    db.session.add_all([math, science])
    db.session.commit()

    # Create Chapters
    algebra = Chapter(name="Algebra", description="Equations and variables", subject_id=math.id)
    geometry = Chapter(name="Geometry", description="Shapes and angles", subject_id=math.id)
    physics = Chapter(name="Physics", description="Motion and forces", subject_id=science.id)
    chemistry = Chapter(name="Chemistry", description="Elements and reactions", subject_id=science.id)
    db.session.add_all([algebra, geometry, physics, chemistry])
    db.session.commit()

    # Create Quizzes
    algebra_quiz = Quiz(chapter_id=algebra.id, date_of_quiz=datetime.now(), time_duration=30, remarks="Basic Algebra Quiz")
    geometry_quiz = Quiz(chapter_id=geometry.id, date_of_quiz=datetime.now(), time_duration=30, remarks="Geometry Basics")
    physics_quiz = Quiz(chapter_id=physics.id, date_of_quiz=datetime.now(), time_duration=30, remarks="Physics Fundamentals")
    chemistry_quiz = Quiz(chapter_id=chemistry.id, date_of_quiz=datetime.now(), time_duration=30, remarks="Introduction to Chemistry")
    db.session.add_all([algebra_quiz, geometry_quiz, physics_quiz, chemistry_quiz])
    db.session.commit()

    # Create Questions
    questions = [
        Question(quiz_id=algebra_quiz.id, question_statement="What is 2 + 2?", option1="3", option2="4", option3="5", option4="6", correct_option="4"),
        Question(quiz_id=algebra_quiz.id, question_statement="Solve for x: 2x = 10", option1="2", option2="3", option3="5", option4="10", correct_option="5"),
        Question(quiz_id=geometry_quiz.id, question_statement="How many sides does a triangle have?", option1="2", option2="3", option3="4", option4="5", correct_option="3"),
        Question(quiz_id=geometry_quiz.id, question_statement="What is the sum of angles in a triangle?", option1="180°", option2="360°", option3="90°", option4="270°", correct_option="180°"),
        Question(quiz_id=physics_quiz.id, question_statement="What is the SI unit of force?", option1="Joule", option2="Newton", option3="Pascal", option4="Watt", correct_option="Newton"),
        Question(quiz_id=physics_quiz.id, question_statement="Which planet is known as the Red Planet?", option1="Earth", option2="Mars", option3="Jupiter", option4="Venus", correct_option="Mars"),
        Question(quiz_id=chemistry_quiz.id, question_statement="What is H2O commonly known as?", option1="Oxygen", option2="Water", option3="Hydrogen", option4="Salt", correct_option="Water"),
        Question(quiz_id=chemistry_quiz.id, question_statement="Which element has the chemical symbol 'O'?", option1="Oxygen", option2="Gold", option3="Silver", option4="Iron", correct_option="Oxygen")
    ]
    db.session.add_all(questions)
    db.session.commit()
