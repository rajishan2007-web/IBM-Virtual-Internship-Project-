def test_student_dashboard_rendering(client, init_database):
    # Log in as Student
    client.post('/login', data={'username': 'ST001', 'password': 'stpass'})

    response = client.get('/student/dashboard')
    assert response.status_code == 200
    assert b'Test Student' in response.data
    assert b'Overall Marks' in response.data
    assert b'Overall Attendance' in response.data
