import re
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy.exc import SQLAlchemyError
from app import db, get_performance_status
from app.models import User, Student, Subject, Marks, Attendance
from app.routes import faculty_required, _student_stats

def _get_or_none(model, pk):
    """Return a model instance by primary key, or None (SQLAlchemy 2.x compatible)."""
    return db.session.get(model, pk)

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.route('/dashboard')
@faculty_required
def dashboard():
    students = Student.query.all()
    subjects = Subject.query.all()
    
    total_students = len(students)
    
    # Calculate overall class averages
    all_marks = Marks.query.all()
    all_att = Attendance.query.all()

    avg_marks = round(sum(m.percentage for m in all_marks) / len(all_marks), 2) if all_marks else 0.0

    total_classes = sum(a.total_classes for a in all_att)
    total_attended = sum(a.classes_attended for a in all_att)
    avg_att = round((total_attended / total_classes * 100.0), 2) if total_classes > 0 else 0.0

    # Count students needing attention or low attendance; build display lists
    low_att_count = 0
    good_count = 0
    needs_attention_count = 0
    attention_students = []
    low_att_students = []   # students whose overall attendance is below 75%

    for s in students:
        s_avg_m, s_avg_a, s_att_cls, s_tot_cls = _student_stats(s.id)

        if s_avg_a < 75.0:
            low_att_count += 1
            low_att_students.append({
                'name':        s.name,
                'reg_number':  s.reg_number,
                'avg_att':     s_avg_a,
                'classes_attended': s_att_cls,
                'total_classes':    s_tot_cls,
            })

        status = get_performance_status(s_avg_a, s_avg_m)
        if status == 'Good Performance':
            good_count += 1
        elif status == 'Needs Attention':
            needs_attention_count += 1
            attention_students.append({
                'name':       s.name,
                'reg_number': s.reg_number,
                'avg_marks':  s_avg_m,
                'avg_att':    s_avg_a,
            })

    return render_template('faculty_dashboard.html',
                           total_students=total_students,
                           total_subjects=len(subjects),
                           avg_marks=avg_marks,
                           avg_att=avg_att,
                           good_count=good_count,
                           low_att_count=low_att_count,
                           needs_attention_count=needs_attention_count,
                           attention_students=attention_students,
                           low_att_students=low_att_students)


@faculty_bp.route('/students', methods=['GET', 'POST'])
@faculty_required
def students():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        reg_number = request.form.get('reg_number', '').strip()
        email = request.form.get('email', '').strip()
        course = request.form.get('course', 'BCA').strip()
        semester = request.form.get('semester', 3, type=int)
        password = request.form.get('password', '').strip()

        if not name or not reg_number or not email or not password:
            flash('All fields are required to register a student.', 'danger')
            return redirect(url_for('faculty.students'))

        if len(name) > 100:
            flash('Student name must be 100 characters or fewer.', 'danger')
            return redirect(url_for('faculty.students'))

        if len(reg_number) > 50:
            flash('Registration number must be 50 characters or fewer.', 'danger')
            return redirect(url_for('faculty.students'))

        if len(email) > 120 or not _EMAIL_RE.match(email):
            flash('Please enter a valid email address (max 120 characters).', 'danger')
            return redirect(url_for('faculty.students'))

        if len(course) > 50:
            flash('Course name must be 50 characters or fewer.', 'danger')
            return redirect(url_for('faculty.students'))

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('faculty.students'))

        existing_user = User.query.filter_by(username=reg_number).first()
        if existing_user:
            flash('A student with that registration number already exists.', 'danger')
            return redirect(url_for('faculty.students'))

        try:
            # Create user and student profile in the same transaction
            # pyrefly: ignore [unexpected-keyword]
            user = User(username=reg_number, role='student')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # pyrefly: ignore [unexpected-keyword]
            student = Student(user_id=user.id, name=name, reg_number=reg_number,
                              email=email, course=course, semester=semester)
            db.session.add(student)
            db.session.flush()

            # Initialize Marks and Attendance records for existing subjects
            subjects = Subject.query.all()
            for subj in subjects:
                # pyrefly: ignore [unexpected-keyword]
                m = Marks(student_id=student.id, subject_id=subj.id,
                          internal_marks=0, assignment_marks=0, final_marks=0)
                m.calculate_total()
                db.session.add(m)
                # pyrefly: ignore [unexpected-keyword]
                att = Attendance(student_id=student.id, subject_id=subj.id,
                                 total_classes=0, classes_attended=0)
                att.calculate_percentage()
                db.session.add(att)

            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Failed to add student %s: %s', reg_number, e)
            flash('A database error occurred while adding the student. Please try again.', 'danger')
            return redirect(url_for('faculty.students'))

        flash(f'Student "{name}" ({reg_number}) added successfully!', 'success')
        return redirect(url_for('faculty.students'))

    student_list = Student.query.all()

    # Build per-student summary for search/filter support in the template.
    # Each entry adds avg_marks, avg_att, and performance_status so the
    # template can embed them as data attributes for client-side filtering.
    students_with_stats = []
    for s in student_list:
        s_avg_m, s_avg_a, *_ = _student_stats(s.id)

        att_status = 'low' if s_avg_a < 75.0 else 'normal'
        perf_status = get_performance_status(s_avg_a, s_avg_m)

        students_with_stats.append({
            'student':      s,
            'avg_marks':    s_avg_m,
            'avg_att':      s_avg_a,
            'att_status':   att_status,
            'perf_status':  perf_status,
        })

    return render_template('students.html', students=student_list, students_with_stats=students_with_stats)


@faculty_bp.route('/subjects', methods=['GET', 'POST'])
@faculty_required
def subjects():
    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        subject_code = request.form.get('subject_code', '').strip().upper()
        semester = request.form.get('semester', 3, type=int)

        if not subject_name or not subject_code:
            flash('Subject name and code are required.', 'danger')
            return redirect(url_for('faculty.subjects'))

        if len(subject_name) > 100:
            flash('Subject name must be 100 characters or fewer.', 'danger')
            return redirect(url_for('faculty.subjects'))

        if len(subject_code) > 20:
            flash('Subject code must be 20 characters or fewer.', 'danger')
            return redirect(url_for('faculty.subjects'))

        existing_subj = Subject.query.filter_by(subject_code=subject_code).first()
        if existing_subj:
            flash(f'Subject with Code "{subject_code}" already exists.', 'danger')
            return redirect(url_for('faculty.subjects'))

        faculty_id = session.get('faculty_id')
        try:
            # pyrefly: ignore [unexpected-keyword]
            subj = Subject(subject_name=subject_name, subject_code=subject_code,
                           semester=semester, faculty_id=faculty_id)
            db.session.add(subj)
            db.session.flush()

            # Automatically create Marks & Attendance entries for existing students
            students = Student.query.all()
            for s in students:
                # pyrefly: ignore [unexpected-keyword]
                m = Marks(student_id=s.id, subject_id=subj.id,
                          internal_marks=0, assignment_marks=0, final_marks=0)
                m.calculate_total()
                db.session.add(m)
                # pyrefly: ignore [unexpected-keyword]
                att = Attendance(student_id=s.id, subject_id=subj.id,
                                 total_classes=0, classes_attended=0)
                att.calculate_percentage()
                db.session.add(att)

            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Failed to add subject %s: %s', subject_code, e)
            flash('A database error occurred while adding the subject. Please try again.', 'danger')
            return redirect(url_for('faculty.subjects'))

        flash(f'Subject "{subject_name}" ({subject_code}) created successfully!', 'success')
        return redirect(url_for('faculty.subjects'))

    subject_list = Subject.query.all()
    return render_template('subjects.html', subjects=subject_list)


@faculty_bp.route('/marks', methods=['GET', 'POST'])
@faculty_required
def marks():
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        internal = request.form.get('internal_marks', 0, type=float)
        assignment = request.form.get('assignment_marks', 0, type=float)
        final = request.form.get('final_marks', 0, type=float)

        if not student_id or not subject_id:
            flash('Please select both a student and a subject.', 'danger')
            return redirect(url_for('faculty.marks'))

        # Verify the referenced records actually exist
        if not _get_or_none(Student, student_id):
            flash('The selected student does not exist.', 'danger')
            return redirect(url_for('faculty.marks'))
        if not _get_or_none(Subject, subject_id):
            flash('The selected subject does not exist.', 'danger')
            return redirect(url_for('faculty.marks'))

        # Validation for mark bounds
        if internal < 0 or internal > 20 or assignment < 0 or assignment > 20 or final < 0 or final > 60:
            flash('Invalid marks range! Max limits: Internal (20), Assignment (20), Final (60).', 'danger')
            return redirect(url_for('faculty.marks'))

        try:
            mark_entry = Marks.query.filter_by(student_id=student_id, subject_id=subject_id).first()
            if not mark_entry:
                # pyrefly: ignore [unexpected-keyword]
                mark_entry = Marks(student_id=student_id, subject_id=subject_id)
                db.session.add(mark_entry)

            mark_entry.internal_marks = internal
            mark_entry.assignment_marks = assignment
            mark_entry.final_marks = final
            mark_entry.calculate_total()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Failed to update marks for student %s subject %s: %s',
                         student_id, subject_id, e)
            flash('A database error occurred while saving marks. Please try again.', 'danger')
            return redirect(url_for('faculty.marks'))

        flash('Student marks updated successfully!', 'success')
        return redirect(url_for('faculty.marks'))

    students = Student.query.all()
    subjects = Subject.query.all()
    marks_list = Marks.query.all()
    return render_template('marks.html', students=students, subjects=subjects, marks_list=marks_list)


@faculty_bp.route('/attendance', methods=['GET', 'POST'])
@faculty_required
def attendance():
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        total_cls = request.form.get('total_classes', 0, type=int)
        attended_cls = request.form.get('classes_attended', 0, type=int)

        if not student_id or not subject_id:
            flash('Please select both a student and a subject.', 'danger')
            return redirect(url_for('faculty.attendance'))

        # Verify the referenced records actually exist
        if not _get_or_none(Student, student_id):
            flash('The selected student does not exist.', 'danger')
            return redirect(url_for('faculty.attendance'))
        if not _get_or_none(Subject, subject_id):
            flash('The selected subject does not exist.', 'danger')
            return redirect(url_for('faculty.attendance'))

        if attended_cls > total_cls or total_cls <= 0 or attended_cls < 0:
            flash('Classes attended cannot exceed total classes or be negative.', 'danger')
            return redirect(url_for('faculty.attendance'))

        try:
            att_entry = Attendance.query.filter_by(student_id=student_id, subject_id=subject_id).first()
            if not att_entry:
                # pyrefly: ignore [unexpected-keyword]
                att_entry = Attendance(student_id=student_id, subject_id=subject_id)
                db.session.add(att_entry)

            att_entry.total_classes = total_cls
            att_entry.classes_attended = attended_cls
            att_entry.calculate_percentage()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Failed to update attendance for student %s subject %s: %s',
                         student_id, subject_id, e)
            flash('A database error occurred while saving attendance. Please try again.', 'danger')
            return redirect(url_for('faculty.attendance'))

        flash('Student attendance updated successfully!', 'success')
        return redirect(url_for('faculty.attendance'))

    students = Student.query.all()
    subjects = Subject.query.all()
    attendance_list = Attendance.query.all()
    return render_template('attendance.html', students=students, subjects=subjects, attendance_list=attendance_list)
