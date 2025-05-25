import os
import re
import ipaddress
import html
import urllib.parse
from datetime import datetime
import pyotp
from flask import request, current_app
from flask_login import current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError

from extensions import db

def create_default_admin():
    """Create a default admin user if no admin exists"""
    try:
        from models import Employee
        if not Employee.query.filter_by(role='admin').first():
            admin = Employee(
                username='admin',
                email='admin@supermarket.com',
                full_name='System Administrator',
                role='admin',
                mfa_secret=pyotp.random_base32()[0:16]
            )
            admin.set_password('Admin@Secure123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created successfully.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error creating default admin: {e}")

def log_security_event(event_type, description, user_id=None, details=None):
    """
    Log a security event to the database.
    
    Args:
        event_type: Type of security event (e.g., 'login_success', 'login_failed')
        description: Human-readable description of the event
        user_id: ID of the associated user (if authenticated)
        details: Dict of additional details to store as JSON
    """
    try:
        from models import SecurityLog
        
        # Get IP address safely
        ip = request.remote_addr
        if ip:
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                ip = 'Invalid IP'
        
        # Get user ID from current_user if not provided
        if user_id is None and current_user.is_authenticated:
            user_id = current_user.id
        
        # Create security log entry
        log = SecurityLog(
            event_type=event_type,
            description=description,
            ip_address=ip,
            user_agent=request.headers.get('User-Agent'),
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        
        # Add additional details if provided
        if details:
            log.set_details(details)
        
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # Don't let logging errors disrupt the application
        db.session.rollback()
        current_app.logger.error(f"Error logging security event: {str(e)}")

def check_account_lock(user):
    """Check if a user account is locked"""
    if user and user.account_locked:
        return True
    return False

def create_security_policies():
    """Create security policies if needed"""
    # Add security policy headers
    pass

def sanitize_input(input_str, max_length=100):
    """
    Basic XSS and SQL injection prevention.
    
    Args:
        input_str: The input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not input_str:
        return ''
    
    # Truncate to max length
    input_str = input_str[:max_length]
    
    # Basic XSS sanitization
    input_str = html.escape(input_str)
    
    # Remove potentially dangerous SQL characters
    input_str = re.sub(r'[\'";]', '', input_str)
    
    return input_str

def is_safe_url(target):
    """
    Check if a URL is safe to redirect to.
    """
    if not target:
        return False
    
    ref_url = urllib.parse.urlparse(request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(request.host_url, target))
    
    # Only allow redirects to the same host
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def parse_sort_param(sort_by, sort_order, allowed_fields=None):

    # Default values
    field = 'id'
    direction = 'asc'
    
    # Validate sort_by
    if sort_by and (allowed_fields is None or sort_by in allowed_fields):
        field = sort_by
    
    # Validate sort_order
    if sort_order and sort_order.lower() in ['asc', 'desc']:
        direction = sort_order.lower()
    
    return field, direction

def validate_request_origin():
    """
    Validate that the request origin is from the same site.
    Helps prevent CSRF attacks in addition to the CSRF tokens.
    """
    origin = request.headers.get('Origin', '')
    host = request.host_url.rstrip('/')
    
    if origin and origin != host and not origin.startswith(host):
        log_security_event('invalid_origin', f'Invalid request origin: {origin}')
        return False
    
    return True
