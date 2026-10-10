from flask import Blueprint, render_template
from app import get_performance_status
from app.models import Student, Subject, Marks, Attendance
from app.routes import faculty_required, _student_stats

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@faculty_required
def index():
    students = Student.query.all()
    subjects = Subject.query.all()

    # Aggregate student analytics list
    student_analytics = []
    
    good_count = 0
    average_count = 0
    attention_count = 0

    for s in students:
        avg_m, avg_a, *_ = _student_stats(s.id)
        status = get_performance_status(avg_a, avg_m)

        if status == 'Good Performance':
            good_count += 1
        elif status == 'Average Performance':
            average_count += 1
        else:
            attention_count += 1

        student_analytics.append({
            'id': s.id,
            'name': s.name,
            'reg_number': s.reg_number,
            'course': s.course,
            'avg_marks': avg_m,
            'avg_att': avg_a,
            'status': status
        })

    # Aggregate subject-wise averages
    subject_analytics = []
    subject_names = []
    subject_avg_marks = []
    subject_avg_att = []

    for subj in subjects:
        m_list = Marks.query.filter_by(subject_id=subj.id).all()
        a_list = Attendance.query.filter_by(subject_id=subj.id).all()

        s_m_avg = round(sum(m.percentage for m in m_list) / len(m_list), 2) if m_list else 0.0
        
        s_tot = sum(a.total_classes for a in a_list)
        s_att = sum(a.classes_attended for a in a_list)
        s_a_avg = round((s_att / s_tot * 100.0), 2) if s_tot > 0 else 0.0

        subject_names.append(subj.subject_code)
        subject_avg_marks.append(s_m_avg)
        subject_avg_att.append(s_a_avg)

        subject_analytics.append({
            'code': subj.subject_code,
            'name': subj.subject_name,
            'avg_marks': s_m_avg,
            'avg_att': s_a_avg
        })

    return render_template('analytics.html',
                           student_analytics=student_analytics,
                           subject_analytics=subject_analytics,
                           good_count=good_count,
                           average_count=average_count,
                           attention_count=attention_count,
                           subject_names=subject_names,
                           subject_avg_marks=subject_avg_marks,
                           subject_avg_att=subject_avg_att)
