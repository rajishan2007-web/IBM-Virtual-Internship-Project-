"""
Database Initialization and Demo Data Seeding Script
Run this script to initialize the SQLite database and load sample demo records.
"""

from app import create_app, db
from app.models import User, Faculty, Student, Subject, Marks, Attendance

def seed_database():
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate clean schema
        db.drop_all()
        db.create_all()

        print("[*] Creating Faculty Account...")
        # 1. Create Faculty
        faculty_user = User(username='prof.smith@college.edu', role='faculty')
        faculty_user.set_password('faculty123')
        db.session.add(faculty_user)
        db.session.flush()

        faculty_profile = Faculty(
            user_id=faculty_user.id,
            name='Prof. Alan Smith',
            email='prof.smith@college.edu',
            department='Computer Applications (BCA)'
        )
        db.session.add(faculty_profile)
        db.session.flush()

        print("[*] Creating 4 Subjects...")
        # 2. Create 4 Subjects
        subjects_data = [
            {'code': 'BCA301', 'name': 'Java Programming', 'sem': 3},
            {'code': 'BCA302', 'name': 'Database Management Systems', 'sem': 3},
            {'code': 'BCA303', 'name': 'Operating Systems', 'sem': 3},
            {'code': 'BCA304', 'name': 'Web Technologies', 'sem': 3}
        ]

        subject_objects = []
        for s in subjects_data:
            subj = Subject(
                subject_name=s['name'],
                subject_code=s['code'],
                semester=s['sem'],
                faculty_id=faculty_profile.id
            )
            db.session.add(subj)
            subject_objects.append(subj)
        db.session.flush()

        print("[*] Creating 5 Students...")
        # 3. Create 5 Students
        students_data = [
            {'reg': 'BCA2024001', 'name': 'Rahul Sharma', 'email': 'rahul@student.edu'},
            {'reg': 'BCA2024002', 'name': 'Priya Verma', 'email': 'priya@student.edu'},
            {'reg': 'BCA2024003', 'name': 'Amit Kumar', 'email': 'amit@student.edu'},
            {'reg': 'BCA2024004', 'name': 'Sneha Gupta', 'email': 'sneha@student.edu'},
            {'reg': 'BCA2024005', 'name': 'Vikram Singh', 'email': 'vikram@student.edu'}
        ]

        student_objects = []
        for st in students_data:
            st_user = User(username=st['reg'], role='student')
            st_user.set_password('student123')
            db.session.add(st_user)
            db.session.flush()

            st_prof = Student(
                user_id=st_user.id,
                name=st['name'],
                reg_number=st['reg'],
                email=st['email'],
                course='BCA',
                semester=3
            )
            db.session.add(st_prof)
            student_objects.append(st_prof)
        db.session.flush()

        print("[*] Seeding Marks and Attendance Records...")
        # 4. Seed Marks & Attendance per student per subject
        # Preset realistic performance profiles:
        # Rahul (Good): High Att, High Marks
        # Priya (Average): High Att, Mid Marks
        # Amit (Needs Attention): Low Att, Low Marks
        # Sneha (Good): High Att, High Marks
        # Vikram (Needs Attention): Low Att, High Marks (Attendance < 75%)

        performance_matrix = {
            'BCA2024001': [
                # Internal (20), Assignment (20), Final (60), Attended, TotalClasses
                (18, 18, 52, 38, 40), # BCA301
                (17, 19, 54, 37, 40), # BCA302
                (19, 18, 50, 39, 40), # BCA303
                (18, 19, 53, 38, 40), # BCA304
            ],
            'BCA2024002': [
                (14, 15, 36, 36, 40), # 65% Marks, 90% Att -> Average
                (13, 14, 35, 35, 40),
                (15, 14, 38, 37, 40),
                (14, 15, 34, 36, 40),
            ],
            'BCA2024003': [
                (10, 10, 24, 25, 40), # 44% Marks, 62.5% Att -> Needs Attention
                (9, 11, 22, 24, 40),
                (8, 10, 26, 26, 40),
                (11, 9, 23, 25, 40),
            ],
            'BCA2024004': [
                (19, 19, 55, 39, 40), # Good
                (18, 18, 56, 38, 40),
                (19, 19, 52, 40, 40),
                (18, 19, 54, 38, 40),
            ],
            'BCA2024005': [
                (17, 18, 50, 26, 40), # 85% Marks, 65% Att (<75%) -> Needs Attention
                (16, 17, 51, 27, 40),
                (18, 16, 49, 28, 40),
                (17, 17, 52, 25, 40),
            ]
        }

        for st_prof in student_objects:
            records = performance_matrix[st_prof.reg_number]
            for idx, subj in enumerate(subject_objects):
                internal, assign, final, att_cls, tot_cls = records[idx]
                
                # Add Marks
                m = Marks(
                    student_id=st_prof.id,
                    subject_id=subj.id,
                    internal_marks=internal,
                    assignment_marks=assign,
                    final_marks=final
                )
                m.calculate_total()
                db.session.add(m)

                # Add Attendance
                att = Attendance(
                    student_id=st_prof.id,
                    subject_id=subj.id,
                    total_classes=tot_cls,
                    classes_attended=att_cls
                )
                att.calculate_percentage()
                db.session.add(att)

        db.session.commit()
        print("[+] Seed process completed successfully!")
        print("    Demo faculty account: prof.smith@college.edu")
        print("    Demo student accounts: BCA2024001 – BCA2024005")
        print("    Credentials are set in this script; do not run against production.")

if __name__ == '__main__':
    seed_database()
