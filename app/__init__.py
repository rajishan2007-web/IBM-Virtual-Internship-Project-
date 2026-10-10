import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[])

def get_performance_status(attendance_pct, marks_pct):
    """
    Performance Classification Rules:
    - Attendance >= 75% and marks >= 70% -> Good Performance
    - Attendance >= 75% and marks between 50% and 69.99% -> Average Performance
    - Attendance < 75% OR marks < 50% -> Needs Attention
    """
    if attendance_pct >= 75.0 and marks_pct >= 70.0:
        return 'Good Performance'
    elif attendance_pct >= 75.0 and 50.0 <= marks_pct < 70.0:
        return 'Average Performance'
    else:
        return 'Needs Attention'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Register performance helper in jinja globals
    app.jinja_env.globals.update(get_performance_status=get_performance_status)

    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.faculty import faculty_bp
    from app.routes.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(analytics_bp)

    # ── Global error handlers ───────────────────────────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        logger.error('Internal server error: %s', e)
        return render_template('errors/500.html'), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template('errors/429.html'), 429

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    return app
