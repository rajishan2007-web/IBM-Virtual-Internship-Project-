import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import limiter
from app.models import User, Student, Faculty

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'faculty':
            return redirect(url_for('faculty.dashboard'))
        elif session.get('role') == 'student':
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter both username/reg number and password.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if not student:
                    session.clear()
                    logger.error('Student profile missing for user_id=%s', user.id)
                    flash('Your account is incomplete. Please contact the administrator.', 'danger')
                    return render_template('login.html')
                session['student_id'] = student.id
                session['name'] = student.name
                flash(f'Welcome back, {student.name}!', 'success')
                return redirect(url_for('student.dashboard'))

            elif user.role == 'faculty':
                faculty = Faculty.query.filter_by(user_id=user.id).first()
                if not faculty:
                    session.clear()
                    logger.error('Faculty profile missing for user_id=%s', user.id)
                    flash('Your account is incomplete. Please contact the administrator.', 'danger')
                    return render_template('login.html')
                session['faculty_id'] = faculty.id
                session['name'] = faculty.name
                flash(f'Welcome back, Prof. {faculty.name}!', 'success')
                return redirect(url_for('faculty.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
