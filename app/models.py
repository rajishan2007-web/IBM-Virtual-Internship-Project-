from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Reg No for Student, Email for Faculty
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'faculty'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), default='BCA')

    user = db.relationship('User', backref=db.backref('faculty_profile', uselist=False))
    subjects = db.relationship('Subject', backref='faculty', lazy=True)

    def __repr__(self):
        return f'<Faculty {self.name}>'


class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    reg_number = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(50), default='BCA')
    semester = db.Column(db.Integer, default=3)

    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))
    marks = db.relationship('Marks', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Student {self.reg_number} - {self.name}>'


class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20), unique=True, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)

    marks = db.relationship('Marks', backref='subject', lazy=True, cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='subject', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Subject {self.subject_code} - {self.subject_name}>'


class Marks(db.Model):
    __tablename__ = 'marks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    internal_marks = db.Column(db.Float, default=0.0)    # e.g., max 20
    assignment_marks = db.Column(db.Float, default=0.0)  # e.g., max 20
    final_marks = db.Column(db.Float, default=0.0)       # e.g., max 60
    total_marks = db.Column(db.Float, default=0.0)       # sum of above
    percentage = db.Column(db.Float, default=0.0)        # total_marks / 100 * 100

    def calculate_total(self):
        """Calculates total marks and percentage (assuming total out of 100)."""
        self.total_marks = float(self.internal_marks or 0) + float(self.assignment_marks or 0) + float(self.final_marks or 0)
        self.percentage = round(self.total_marks, 2)
        return self.total_marks

    def __repr__(self):
        return f'<Marks Student:{self.student_id} Subject:{self.subject_id} Total:{self.total_marks}>'


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    total_classes = db.Column(db.Integer, default=0)
    classes_attended = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)

    def calculate_percentage(self):
        """Calculates attendance percentage automatically."""
        if self.total_classes > 0:
            pct = (float(self.classes_attended) / float(self.total_classes)) * 100.0
            self.percentage = round(pct, 2)
        else:
            self.percentage = 0.0
        return self.percentage

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Subject:{self.subject_id} {self.percentage}%>'
