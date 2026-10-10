# Student Performance & Attendance Analytics System (SPAS)

A web application built with Python Flask that enables a faculty member to manage student academic records and allows each student to view their own academic summary. The system tracks marks across three assessment types and records class attendance per subject, then derives a performance classification from the combined results.

> **Note:** This project was created with the help of **IBM BOB**.

---

## Problem Statement

Tracking student academic performance manually across multiple subjects is error-prone and time-consuming. Faculty need a single place to record marks and attendance, see which students are falling behind, and identify attendance shortfalls. Students need a clear, personal view of where they stand — without access to anyone else's data.

---

## Objectives

- Give faculty one interface to register students, define subjects, and record marks and attendance.
- Automatically compute totals, percentages, and a three-tier performance classification whenever data is saved.
- Give each student a read-only dashboard showing their own subject-wise and overall academic position.
- Provide a faculty-only analytics view showing performance distribution across all students and subjects.
- Separate access strictly by role: faculty manage all records; a student can only see their own.

---

## Features

### Faculty

| Feature | Detail |
|---|---|
| **Dashboard** | Displays total students, total subjects, class-average marks %, class-average attendance %, a list of students below 75% attendance, and a list of students classified as Needs Attention |
| **Student management** | Register new students via a modal form; view all students in a searchable and filterable table (filter by name, registration number, performance status, attendance status) |
| **Subject management** | Add new subjects; view all subjects with their assigned faculty |
| **Marks entry** | Enter or update Internal (max 20), Assignment (max 20), and Final (max 60) marks per student per subject; totals and percentages are computed automatically |
| **Attendance entry** | Enter or update total classes conducted and classes attended per student per subject; percentage is computed automatically |
| **Analytics** | Per-student table of average marks %, average attendance %, and performance classification; per-subject averages; count breakdown of Good / Average / Needs Attention; Chart.js bar and line charts |

### Student

| Feature | Detail |
|---|---|
| **Personal dashboard** | Subject-wise table showing internal, assignment, final, total marks, marks %, total classes, attended classes, attendance %, and per-subject performance status |
| **Overall metrics** | Overall marks % and overall attendance % computed from raw totals across all subjects |
| **Charts** | Chart.js visualisation of per-subject marks and attendance (data passed from server as JSON arrays) |

### Performance classification

| Label | Condition |
|---|---|
| **Good Performance** | Attendance ≥ 75% **and** Marks ≥ 70% |
| **Average Performance** | Attendance ≥ 75% **and** 50% ≤ Marks < 70% |
| **Needs Attention** | Attendance < 75% **or** Marks < 50% |

---

## Technologies Used

| Technology | Version | Role |
|---|---|---|
| Python | 3.x | Runtime |
| Flask | 3.0.3 | Web framework — routing, templating, sessions, blueprints |
| Flask-SQLAlchemy | 3.1.1 | ORM; all database access goes through SQLAlchemy models |
| Werkzeug | 3.0.3 | PBKDF2-SHA256 password hashing |
| Flask-WTF | 1.3.0 | CSRF token generation and validation on all POST forms |
| Flask-Limiter | 4.1.1 | Per-IP rate limiting on the login endpoint (10 req/min) |
| SQLite | stdlib | File-based relational database (`instance/database.db`) |
| Bootstrap | 5.3.3 (CDN) | UI framework and component library |
| Bootstrap Icons | 1.11.3 (CDN) | Icon set |
| Chart.js | latest (CDN) | Bar and line charts on dashboards and analytics page |
| pytest | 8.2.2 | Test runner |

---

## Project Structure

```
├── run.py                  # Entry point — starts the development server
├── config.py               # Config class (SECRET_KEY, DB URI, cookie flags, CSRF)
├── seed.py                 # One-time demo data seeder
├── requirements.txt
├── instance/
│   └── database.db         # SQLite file, created automatically at runtime
├── tests/
│   ├── conftest.py         # pytest fixtures
│   ├── test_auth.py
│   ├── test_calculations.py
│   ├── test_faculty.py
│   └── test_student.py
└── app/
    ├── __init__.py         # App factory, extensions, global error handlers
    ├── models.py           # SQLAlchemy models
    ├── templates/
    │   ├── base.html
    │   ├── login.html
    │   ├── faculty_dashboard.html
    │   ├── students.html
    │   ├── subjects.html
    │   ├── marks.html
    │   ├── attendance.html
    │   ├── analytics.html
    │   ├── student_dashboard.html
    │   └── errors/
    │       ├── 403.html
    │       ├── 404.html
    │       ├── 429.html
    │       └── 500.html
    └── routes/
        ├── __init__.py     # Role decorators, shared stats helper
        ├── auth.py         # /, /login, /logout
        ├── faculty.py      # /faculty/* (dashboard, students, subjects, marks, attendance)
        ├── student.py      # /student/dashboard
        └── analytics.py    # /analytics/
```

---

## Installation

### Prerequisites

- Python 3.8 or later
- `pip`

### Steps

**1. Clone the repository**

```bash
git clone <repository-url>
cd <project-folder>
```

**2. Create and activate a virtual environment**

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set the required environment variable**

`SECRET_KEY` is mandatory. The application will not start without it.

```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"

# macOS / Linux — set for the current shell session
export SECRET_KEY="paste-your-generated-key-here"

# Windows (Command Prompt)
set SECRET_KEY=paste-your-generated-key-here

# Windows (PowerShell)
$env:SECRET_KEY = "paste-your-generated-key-here"
```

> **Note:** `SESSION_COOKIE_SECURE = True` is set in `Config`, which requires HTTPS. For local development over plain HTTP, either set this to `False` in `config.py` or use a tool like [mkcert](https://github.com/FiloSottile/mkcert) to run a local HTTPS server.

---

## Database Setup

The database file is created automatically the first time the application starts. To populate it with demo data (1 faculty, 5 students, 4 subjects, and pre-filled marks and attendance records), run the seed script **once**:

```bash
python seed.py
```

> **Warning:** `seed.py` drops and recreates all tables. Do not run it against a database that contains data you want to keep.

Expected output:

```
[*] Creating Faculty Account...
[*] Creating 4 Subjects...
[*] Creating 5 Students...
[*] Seeding Marks and Attendance Records...
[+] Seed process completed successfully!
    Demo faculty account: prof.smith@college.edu
    Demo student accounts: BCA2024001 – BCA2024005
    Credentials are set in this script; do not run against production.
```

---

## Running the Application

```bash
python run.py
```

The server starts at **http://127.0.0.1:5000**.

To enable debug mode (development only — never in production):

```bash
# macOS / Linux
FLASK_DEBUG=true python run.py

# Windows (PowerShell)
$env:FLASK_DEBUG = "true"; python run.py
```

---

## Demo Credentials

These credentials are created by `seed.py`.

### Faculty

| Field | Value |
|---|---|
| Username | `prof.smith@college.edu` |
| Password | `faculty123` |

### Students

All five students share the password `student123`. Each demonstrates a different performance profile.

| Username | Name | Profile |
|---|---|---|
| `BCA2024001` | Rahul Sharma | Good Performance |
| `BCA2024002` | Priya Verma | Average Performance |
| `BCA2024003` | Amit Kumar | Needs Attention (low marks and low attendance) |
| `BCA2024004` | Sneha Gupta | Good Performance |
| `BCA2024005` | Vikram Singh | Needs Attention (attendance below 75%) |

---

## Running the Tests

The test suite uses an in-memory SQLite database and does not require the `SECRET_KEY` environment variable to be set for production — the `TestConfig` fixture supplies its own.

```bash
# Set SECRET_KEY so the production Config can be imported without error
# (only needed because config.py is imported at module level)

# macOS / Linux
SECRET_KEY=test-key python -m pytest tests/ -v

# Windows (PowerShell)
$env:SECRET_KEY = "test-key"; python -m pytest tests/ -v
```

Expected output:

```
tests/test_auth.py::test_login_page_renders          PASSED
tests/test_auth.py::test_faculty_login_success       PASSED
tests/test_auth.py::test_student_login_success       PASSED
tests/test_auth.py::test_invalid_login               PASSED
tests/test_auth.py::test_unauthorized_access         PASSED
tests/test_auth.py::test_logout                      PASSED
tests/test_calculations.py::test_marks_calculation          PASSED
tests/test_calculations.py::test_attendance_calculation     PASSED
tests/test_calculations.py::test_performance_classification_rules PASSED
tests/test_faculty.py::test_add_student_by_faculty   PASSED
tests/test_faculty.py::test_add_subject_by_faculty   PASSED
tests/test_faculty.py::test_update_marks_and_attendance PASSED
tests/test_student.py::test_student_dashboard_rendering PASSED

13 passed
```

### What the tests cover

| File | Tests | Coverage |
|---|---|---|
| `test_auth.py` | 6 | Login page renders; faculty and student login success; wrong password rejected; unauthenticated access denied; logout clears session |
| `test_calculations.py` | 3 | Marks total and percentage formula; attendance percentage including zero-class guard; all performance classification boundary cases |
| `test_faculty.py` | 3 | Add student (DB row verified); add subject (DB row verified); update marks (total verified at 85.0) and attendance (percentage verified at 90.0) |
| `test_student.py` | 1 | Student dashboard renders with student name, overall marks, and overall attendance |

---

## Security Notes

The following controls are implemented in the current codebase:

- **Passwords** — hashed with PBKDF2-SHA256 via Werkzeug; never stored in plain text.
- **Secret key** — mandatory environment variable; the application refuses to start without it.
- **Session cookies** — `Secure`, `HttpOnly`, `SameSite=Lax`, 1-hour lifetime.
- **CSRF protection** — Flask-WTF `CSRFProtect` active on all POST forms.
- **Login rate limiting** — 10 requests/minute per IP; returns HTTP 429 on breach.
- **Role isolation** — `@faculty_required` and `@student_required` decorators on every protected route.
- **Student identity** — resolved from the signed `user_id` in session, never from a URL parameter.
- **Input validation** — server-side length and format checks on all form fields; numeric range checks on marks and attendance values.
- **Atomic transactions** — all write operations use a single `try/except SQLAlchemyError` block with rollback on failure.
- **Error pages** — custom templates for 403, 404, 429, and 500; the 500 handler calls `db.session.rollback()`.
- **SQL injection** — all database access via SQLAlchemy ORM; no raw SQL string concatenation.
- **XSS** — Jinja2 auto-escaping enabled by default for all `.html` templates.

---

## Future Scope

The following features are **not** implemented in the current version:

- Password reset flow for students
- Account lockout after repeated failed login attempts
- Edit and delete operations for students and subjects through the UI
- Multiple faculty accounts with per-faculty subject ownership
- Bulk marks/attendance import from CSV
- Configurable performance thresholds (currently hard-coded at 75% / 70% / 50%)
- Multi-semester / academic-year segmentation (the `semester` field is stored but not filtered on)
- Production WSGI server configuration (gunicorn / uWSGI)
- Persistent rate-limit storage backend (Redis) for multi-process deployments
- Expanded test coverage for validation rejection paths, analytics route, and error rollback paths

---

## Acknowledgements

This project was made with the help of **IBM BOB**.

