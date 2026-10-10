import pytest
from app import create_app, db
from app.models import User, Faculty, Student, Subject, Marks, Attendance

class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    # Setup test faculty
    # pyrefly: ignore [unexpected-keyword]
    fac_user = User(username='fac@test.com', role='faculty')
    fac_user.set_password('facpass')
    db.session.add(fac_user)
    db.session.flush()

    # pyrefly: ignore [unexpected-keyword]
    fac = Faculty(user_id=fac_user.id, name='Dr. Test', email='fac@test.com')
    db.session.add(fac)

    # Setup test student
    # pyrefly: ignore [unexpected-keyword]
    st_user = User(username='ST001', role='student')
    st_user.set_password('stpass')
    db.session.add(st_user)
    db.session.flush()

    # pyrefly: ignore [unexpected-keyword]
    st = Student(user_id=st_user.id, name='Test Student', reg_number='ST001', email='st@test.com', semester=3)
    db.session.add(st)

    # Setup test subject
    # pyrefly: ignore [unexpected-keyword]
    subj = Subject(subject_name='Test Subject', subject_code='TS101', semester=3, faculty_id=fac.id)
    db.session.add(subj)

    db.session.commit()
    return {'fac': fac, 'student': st, 'subject': subj}
