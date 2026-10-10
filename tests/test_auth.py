def test_login_page_renders(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'System Login' in response.data

def test_faculty_login_success(client, init_database):
    response = client.post('/login', data={
        'username': 'fac@test.com',
        'password': 'facpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Faculty Dashboard' in response.data

def test_student_login_success(client, init_database):
    response = client.post('/login', data={
        'username': 'ST001',
        'password': 'stpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Student' in response.data

def test_invalid_login(client, init_database):
    response = client.post('/login', data={
        'username': 'ST001',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_unauthorized_access(client):
    # Try accessing protected faculty & student dashboards without logging in
    response = client.get('/faculty/dashboard', follow_redirects=True)
    assert b'Access denied' in response.data or b'Please log in first' in response.data

    response_st = client.get('/student/dashboard', follow_redirects=True)
    assert b'Access denied' in response_st.data or b'Please log in first' in response_st.data

def test_logout(client, init_database):
    client.post('/login', data={'username': 'ST001', 'password': 'stpass'})
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out successfully' in response.data
