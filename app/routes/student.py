import logging
from flask import Blueprint, render_template, session
from app.models import Student, Marks, Attendance, Subject
from app.routes import student_required
from app import db, get_performance_status

logger = logging.getLogger(__name__)

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@student_required
def dashboard():
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first_or_404()

    # Fetch marks & attendance for all enrolled subjects
    marks_records = Marks.query.filter_by(student_id=student.id).all()
    attendance_records = Attendance.query.filter_by(student_id=student.id).all()

    # Create subject-wise mapping
    subjects_data = []
    total_marks_pct = 0.0
    marks_count = 0

    total_classes_sum = 0
    attended_sum = 0

    chart_labels = []
    chart_marks = []
    chart_attendance = []

    # Map attendance by subject_id for easy lookup
    att_map = {att.subject_id: att for att in attendance_records}

    for m in marks_records:
        subj = db.session.get(Subject, m.subject_id)
        if not subj:
            logger.warning(
                'Marks record id=%s references missing subject_id=%s for student_id=%s — skipping',
                m.id, m.subject_id, student.id
            )
            continue

        att = att_map.get(m.subject_id)
        att_pct = att.percentage if att else 0.0
        
        if att:
            total_classes_sum += att.total_classes
            attended_sum += att.classes_attended

        total_marks_pct += m.percentage
        marks_count += 1

        chart_labels.append(subj.subject_name)
        chart_marks.append(m.percentage)
        chart_attendance.append(att_pct)

        subjects_data.append({
            'subject_name': subj.subject_name,
            'subject_code': subj.subject_code,
            'internal': m.internal_marks,
            'assignment': m.assignment_marks,
            'final': m.final_marks,
            'total': m.total_marks,
            'percentage': m.percentage,
            'total_classes': att.total_classes if att else 0,
            'classes_attended': att.classes_attended if att else 0,
            'att_percentage': att_pct,
            'status': get_performance_status(att_pct, m.percentage)
        })

    # Overall Metrics Calculation
    overall_marks = round(total_marks_pct / marks_count, 2) if marks_count > 0 else 0.0
    overall_att = round((attended_sum / total_classes_sum * 100.0), 2) if total_classes_sum > 0 else 0.0
    overall_status = get_performance_status(overall_att, overall_marks)

    return render_template('student_dashboard.html',
                           student=student,
                           subjects_data=subjects_data,
                           overall_marks=overall_marks,
                           overall_att=overall_att,
                           overall_status=overall_status,
                           subject_count=len(subjects_data),
                           chart_labels=chart_labels,
                           chart_marks=chart_marks,
                           chart_attendance=chart_attendance)
