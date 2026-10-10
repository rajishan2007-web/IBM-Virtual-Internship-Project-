"""
Main Application Runner
Executes the Flask development server.
"""

import os
from app import create_app
from config import Config, DevConfig

debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
app = create_app(DevConfig if debug else Config)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=debug)
