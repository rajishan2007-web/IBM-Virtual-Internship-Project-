from app.models import Marks, Attendance
from app import get_performance_status

def test_marks_calculation():
    # pyrefly: ignore [unexpected-keyword]
    m = Marks(internal_marks=18.5, assignment_marks=17.5, final_marks=48.0)
    total = m.calculate_total()
    assert total == 84.0
    assert m.percentage == 84.0

def test_attendance_calculation():
    # pyrefly: ignore [unexpected-keyword]
    att = Attendance(total_classes=40, classes_attended=34)
    pct = att.calculate_percentage()
    assert pct == 85.0

    # Zero classes test
    # pyrefly: ignore [unexpected-keyword]
    att_zero = Attendance(total_classes=0, classes_attended=0)
    assert att_zero.calculate_percentage() == 0.0

def test_performance_classification_rules():
    # Good Performance
    assert get_performance_status(80.0, 75.0) == 'Good Performance'
    assert get_performance_status(75.0, 70.0) == 'Good Performance'

    # Average Performance
    assert get_performance_status(80.0, 65.0) == 'Average Performance'
    assert get_performance_status(75.0, 50.0) == 'Average Performance'

    # Needs Attention (low marks or low attendance)
    assert get_performance_status(80.0, 45.0) == 'Needs Attention'
    assert get_performance_status(70.0, 85.0) == 'Needs Attention'
    assert get_performance_status(60.0, 40.0) == 'Needs Attention'
