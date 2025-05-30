from app import app, db
from models import Subject, Chapter, Quiz, Question
from datetime import datetime

with app.app_context():
    # Clear old data (optional, be careful!)
    db.drop_all()
    db.create_all()

    # Create Subjects
    math = Subject(name="Mathematics", description="Study of numbers, shapes, and patterns.")
    physics = Subject(name="Physics", description="Study of matter, energy, and forces.")
    db.session.add_all([math, physics])
    db.session.commit()

    # Create Chapters
    algebra = Chapter(name="Algebra", description="Algebra basics", subject_id=math.id)
    geometry = Chapter(name="Geometry", description="Study of shapes", subject_id=math.id)
    mechanics = Chapter(name="Mechanics", description="Motion and forces", subject_id=physics.id)
    db.session.add_all([algebra, geometry, mechanics])
    db.session.commit()

    # Create Quizzes
    algebra_quiz = Quiz(chapter_id=algebra.id, date_of_quiz=datetime.now(), time_duration="30 mins", remarks="Algebra Quiz 1")
    geometry_quiz = Quiz(chapter_id=geometry.id, date_of_quiz=datetime.now(), time_duration="20 mins", remarks="Geometry Basics")
    mechanics_quiz = Quiz(chapter_id=mechanics.id, date_of_quiz=datetime.now(), time_duration="25 mins", remarks="Forces and Motion")
    db.session.add_all([algebra_quiz, geometry_quiz, mechanics_quiz])
    db.session.commit()

    # Create Questions for Algebra Quiz
    q1 = Question(
        quiz_id=algebra_quiz.id,
        question_statement="What is 2 + 2?",
        option1="3",
        option2="4",
        option3="5",
        option4="6",
        correct_option="4"
    )
    q2 = Question(
        quiz_id=algebra_quiz.id,
        question_statement="Solve for x: 2x = 6",
        option1="1",
        option2="2",
        option3="3",
        option4="4",
        correct_option="3"
    )
    q3 = Question(
        quiz_id=geometry_quiz.id,
        question_statement="How many sides does a triangle have?",
        option1="2",
        option2="3",
        option3="4",
        option4="5",
        correct_option="3"
    )
    q4 = Question(
        quiz_id=mechanics_quiz.id,
        question_statement="What is the unit of force?",
        option1="Newton",
        option2="Joule",
        option3="Pascal",
        option4="Watt",
        correct_option="Newton"
    )

    db.session.add_all([q1, q2, q3, q4])
    db.session.commit()

    print("✅ Dummy data inserted successfully!")
