from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, StudentCard, Course, Semester, Result, ScheduleEntry, News
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university_capital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_123')

db.init_app(app)

ADMIN_USERNAME = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PW_HASH')
if not ADMIN_PASSWORD_HASH:
    ADMIN_PASSWORD_HASH = generate_password_hash('adminpass')

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    lang = request.args.get('lang', 'ar')
    news_list = News.query.filter_by(published=True).order_by(News.created_at.desc()).limit(6).all()
    return render_template('home.html', news=news_list, lang=lang)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        card_number = request.form.get('card_number','').strip()
        if not card_number:
            flash("أدخل رقم البطاقة.", "danger")
            return redirect(url_for('login'))
        card = StudentCard.query.filter_by(card_number=card_number).first()
        if not card or not card.active:
            flash("رقم البطاقة غير مسجل أو غير مفعل.", "danger")
            return redirect(url_for('login'))
        session.clear()
        session['student_id'] = card.id
        session['student_name'] = card.student_name
        session['lang'] = request.form.get('lang','ar')
        flash("تم تسجيل الدخول.", "success")
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    student_id = session.get('student_id')
    if not student_id:
        flash("الرجاء تسجيل الدخول برقم البطاقة.", "warning")
        return redirect(url_for('login'))
    card = StudentCard.query.get(student_id)
    results = Result.query.filter_by(student_id=student_id).order_by(Result.date_recorded.desc()).all()
    semesters = {}
    for r in results:
        sem = Semester.query.get(r.semester_id)
        semesters.setdefault(sem.name if sem else "غير معروف", []).append(r)
    return render_template('dashboard.html', card=card, semesters=semesters, lang=session.get('lang','ar'))

@app.route('/my/schedule')
def my_schedule():
    student_id = session.get('student_id')
    if not student_id:
        flash("تحتاج تسجيل دخول.", "warning")
        return redirect(url_for('login'))
    card = StudentCard.query.get(student_id)
    entries = ScheduleEntry.query.filter_by(department=card.department).all()
    return render_template('my_schedule.html', entries=entries, card=card)

@app.route('/my/results')
def my_results():
    student_id = session.get('student_id')
    if not student_id:
        flash("تحتاج تسجيل دخول.", "warning")
        return redirect(url_for('login'))
    card = StudentCard.query.get(student_id)
    results = Result.query.filter_by(student_id=student_id).order_by(Result.date_recorded.desc()).all()
    semesters = {}
    for r in results:
        sem = Semester.query.get(r.semester_id)
        semesters.setdefault(sem.name if sem else "غير معروف", []).append(r)
    return render_template('my_results.html', semesters=semesters, card=card)

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج.", "success")
    return redirect(url_for('home'))

# ----------------- Admin -----------------
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin'] = True
            flash("تم تسجيل دخول الإدارة.", "success")
            return redirect(url_for('admin_panel'))
        flash("بيانات الإدارة غير صحيحة.", "danger")
    return render_template('admin_login.html')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            flash("تحتاج دخول إدارة.", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/panel')
@admin_required
def admin_panel():
    students = StudentCard.query.all()
    courses = Course.query.all()
    semesters = Semester.query.all()
    news = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin_panel.html', students=students, courses=courses, semesters=semesters, news=news)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash("تم خروج الادارة.", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
