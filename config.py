import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for session security — MUST be set via environment variable.
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Session cookie security
    SESSION_COOKIE_SECURE   = True   # Transmit over HTTPS only
    SESSION_COOKIE_HTTPONLY = True   # Block JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # Mitigate CSRF on cross-site requests
    PERMANENT_SESSION_LIFETIME = 3600  # 1-hour session expiry

    # SQLite Database Configuration
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF protection (Flask-WTF)
    WTF_CSRF_ENABLED = True


class DevConfig(Config):
    """
    Development override — use when running locally over plain HTTP.
    Set FLASK_ENV=development (or FLASK_DEBUG=true) and pass this class
    to create_app(), or start with:
        python -c "from config import DevConfig; ..."
    SESSION_COOKIE_SECURE must be False over HTTP or the browser will
    not send the session cookie and every protected route will redirect
    back to /login.
    """
    SESSION_COOKIE_SECURE = False
