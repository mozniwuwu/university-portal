from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class StudentCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(64), unique=True, nullable=False)
    student_name = db.Column(db.String(150))
    department = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    title_ar = db.Column(db.String(200))
    title_en = db.Column(db.String(200))
    department = db.Column(db.String(100))
    is_general = db.Column(db.Boolean, default=False)

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_card.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    grade = db.Column(db.String(20))
    date_recorded = db.Column(db.Date)

class ScheduleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100))
    day = db.Column(db.String(20))
    time_from = db.Column(db.String(20))
    time_to = db.Column(db.String(20))
    room = db.Column(db.String(50))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(300))
    content_ar = db.Column(db.Text)
    title_en = db.Column(db.String(300))
    content_en = db.Column(db.Text)
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.Date)
