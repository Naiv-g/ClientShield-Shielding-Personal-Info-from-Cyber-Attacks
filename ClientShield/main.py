from flask import Flask
from extensions import db, login_manager, csrf
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create and configure the app
app = Flask(__name__)

# Load configuration based on environment
from config import DevelopmentConfig
app.config.from_object(DevelopmentConfig)

# Set secret key
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(32))

# Initialize extensions
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'danger'
login_manager.session_protection = "strong"

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Create database tables and register routes
with app.app_context():
    from models import Employee, Inventory, Client, SecurityLog
    db.create_all()
    
    # Add custom template filters for normal date display
    @app.template_filter('display_date')
    def display_date(date_obj):
        """Custom filter to display date normally"""
        if date_obj:
            return date_obj.strftime('%Y-%m-%d')
        return '-'

    @app.template_filter('display_datetime')
    def display_datetime(date_obj):
        """Custom filter to display datetime normally"""
        if date_obj:
            return date_obj.strftime('%Y-%m-%d %H:%M')
        return '-'
    
    # Register blueprint
    from routes import bp
    app.register_blueprint(bp)
    
    # Initialize default data
    from utils import create_default_admin, create_security_policies
    create_default_admin()
    create_security_policies()

# Run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
