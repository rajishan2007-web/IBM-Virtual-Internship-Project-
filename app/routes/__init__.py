from functools import wraps
from flask import session, redirect, url_for, flash
from app.models import Marks, Attendance


def _student_stats(student_id):
    """Return (avg_marks_pct, avg_attendance_pct, classes_attended, total_classes) for a student."""
    marks = Marks.query.filter_by(student_id=student_id).all()
    att   = Attendance.query.filter_by(student_id=student_id).all()
    avg_m = round(sum(m.percentage for m in marks) / len(marks), 2) if marks else 0.0
    tot   = sum(a.total_classes    for a in att)
    done  = sum(a.classes_attended for a in att)
    avg_a = round(done / tot * 100.0, 2) if tot > 0 else 0.0
    return avg_m, avg_a, done, tot


def faculty_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'faculty':
            flash('Access denied. Faculty login required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            flash('Access denied. Student login required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
