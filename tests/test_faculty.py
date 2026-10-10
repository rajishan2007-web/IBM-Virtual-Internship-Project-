from app.models import Student, Subject, Marks, Attendance

def test_add_student_by_faculty(client, init_database):
    # Log in as faculty
    client.post('/login', data={'username': 'fac@test.com', 'password': 'facpass'})
    
    response = client.post('/faculty/students', data={
        'name': 'New Student',
        'reg_number': 'ST002',
        'email': 'st2@test.com',
        'course': 'BCA',
        'semester': '3',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'added successfully' in response.data

    # Verify student exists in DB
    st = Student.query.filter_by(reg_number='ST002').first()
    assert st is not None
    assert st.name == 'New Student'

def test_add_subject_by_faculty(client, init_database):
    client.post('/login', data={'username': 'fac@test.com', 'password': 'facpass'})

    response = client.post('/faculty/subjects', data={
        'subject_name': 'Data Structures',
        'subject_code': 'DS102',
        'semester': '3'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'created successfully' in response.data

    subj = Subject.query.filter_by(subject_code='DS102').first()
    assert subj is not None

def test_update_marks_and_attendance(client, init_database):
    client.post('/login', data={'username': 'fac@test.com', 'password': 'facpass'})

    st = init_database['student']
    subj = init_database['subject']

    # Update Marks
    m_resp = client.post('/faculty/marks', data={
        'student_id': st.id,
        'subject_id': subj.id,
        'internal_marks': '18',
        'assignment_marks': '17',
        'final_marks': '50'
    }, follow_redirects=True)
    assert b'updated successfully' in m_resp.data

    m_entry = Marks.query.filter_by(student_id=st.id, subject_id=subj.id).first()
    assert m_entry.total_marks == 85.0

    # Update Attendance
    a_resp = client.post('/faculty/attendance', data={
        'student_id': st.id,
        'subject_id': subj.id,
        'total_classes': '40',
        'classes_attended': '36'
    }, follow_redirects=True)
    assert b'updated successfully' in a_resp.data

    a_entry = Attendance.query.filter_by(student_id=st.id, subject_id=subj.id).first()
    assert a_entry.percentage == 90.0
