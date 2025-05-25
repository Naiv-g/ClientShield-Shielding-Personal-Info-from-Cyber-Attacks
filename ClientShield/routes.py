from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort, g
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import urllib.parse
import re

from extensions import db, login_manager
from models import Employee, Inventory, Client, SecurityLog
from forms import (LoginForm, RegistrationForm, InventoryForm, ClientForm, SearchForm, 
                   ChangePasswordForm, ProfileForm)
from utils import log_security_event, check_account_lock, sanitize_input, is_safe_url, parse_sort_param

# Create blueprint
bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

# Basic routes
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(username=form.username.data).first()
        
        if check_account_lock(user):
            flash('Account locked due to multiple failed attempts. Contact admin.', 'danger')
            log_security_event('account_locked', f'Account locked for user: {form.username.data}')
            return render_template('login.html', form=form)
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_security_event('login_success', f'Successful login for {user.username}', user_id=user.id)
            
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.account_locked = True
                    log_security_event('account_locked', f'Account locked for {user.username}')
                db.session.commit()
            log_security_event('login_failed', f'Failed login attempt for {form.username.data}')
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    log_security_event('logout', f'User {current_user.username} logged out', user_id=current_user.id)
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get counts for dashboard stats
    inventory_count = Inventory.query.count()
    client_count = Client.query.count()
    employee_count = Employee.query.count()
    
    # Get low stock items
    low_stock = Inventory.query.filter(Inventory.quantity < 10).all()
    
    # Get recent security logs
    security_logs = SecurityLog.query.order_by(SecurityLog.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          inventory_count=inventory_count,
                          client_count=client_count,
                          employee_count=employee_count,
                          low_stock=low_stock,
                          security_logs=security_logs)

# Inventory routes
@bp.route('/inventory')
@login_required
def inventory():
    search_form = SearchForm()
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Process search filters
    query = request.args.get('query', '')
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Sanitize and validate inputs
    query = sanitize_input(query)
    sort_field, sort_direction = parse_sort_param(sort_by, sort_order, 
                                                  allowed_fields=['name', 'category', 'quantity', 'price'])
    
    # Build query
    items_query = Inventory.query
    
    if query:
        items_query = items_query.filter(Inventory.name.ilike(f'%{query}%'))
    
    if category and category != 'all':
        items_query = items_query.filter(Inventory.category == category)
    
    # Apply sorting
    if sort_direction == 'asc':
        items_query = items_query.order_by(getattr(Inventory, sort_field).asc())
    else:
        items_query = items_query.order_by(getattr(Inventory, sort_field).desc())
    
    # Paginate results
    pagination = items_query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # Get categories for filter
    categories = [c for c, in db.session.query(Inventory.category).distinct()]
    
    return render_template('inventory.html', items=items, pagination=pagination, 
                           search_form=search_form, query=query, current_category=category,
                           categories=categories, sort_by=sort_by, sort_order=sort_order)

@bp.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    form = InventoryForm()
    if form.validate_on_submit():
        try:
            item = Inventory(
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                price=form.price.data,
                quantity=form.quantity.data,
                supplier=form.supplier.data,
                barcode=form.barcode.data,
                updated_by=current_user.id
            )
            db.session.add(item)
            db.session.commit()
            
            log_security_event('inventory_created', f'Inventory item created: {item.name}', user_id=current_user.id)
            
            flash(f'Item "{item.name}" has been added successfully!', 'success')
            return redirect(url_for('main.inventory'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding inventory item: {str(e)}', 'danger')
    
    return render_template('add_inventory.html', form=form)

@bp.route('/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(item_id):
    item = Inventory.query.get_or_404(item_id)
    form = InventoryForm(obj=item)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(item)
            item.updated_by = current_user.id
            item.last_updated = datetime.utcnow()
            db.session.commit()
            
            log_security_event('inventory_updated', f'Inventory item updated: {item.name}', user_id=current_user.id)
            
            flash(f'Item "{item.name}" has been updated successfully!', 'success')
            return redirect(url_for('main.inventory'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating inventory item: {str(e)}', 'danger')
    
    return render_template('edit_inventory.html', form=form, item=item)

@bp.route('/inventory/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_inventory(item_id):
    item = Inventory.query.get_or_404(item_id)
    item_name = item.name
    
    try:
        db.session.delete(item)
        db.session.commit()
        
        log_security_event('inventory_deleted', f'Inventory item deleted: {item_name}', user_id=current_user.id)
        
        flash(f'Item "{item_name}" has been deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting inventory item: {str(e)}', 'danger')
    
    return redirect(url_for('main.inventory'))

# Client routes
@bp.route('/clients')
@login_required
def clients():
    search_form = SearchForm()
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Process search filters
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'last_name')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Sanitize and validate inputs
    query = sanitize_input(query)
    sort_field, sort_direction = parse_sort_param(sort_by, sort_order, 
                                                 allowed_fields=['first_name', 'last_name', 'email', 'city'])
    
    # Build query
    clients_query = Client.query
    
    if query:
        clients_query = clients_query.filter(
            (Client.first_name.ilike(f'%{query}%')) | 
            (Client.last_name.ilike(f'%{query}%')) | 
            (Client.email.ilike(f'%{query}%'))
        )
    
    # Apply sorting
    if sort_direction == 'asc':
        clients_query = clients_query.order_by(getattr(Client, sort_field).asc())
    else:
        clients_query = clients_query.order_by(getattr(Client, sort_field).desc())
    
    # Paginate results
    pagination = clients_query.paginate(page=page, per_page=per_page, error_out=False)
    client_list = pagination.items
    
    return render_template('clients.html', clients=client_list, pagination=pagination, 
                           search_form=search_form, query=query, sort_by=sort_by, sort_order=sort_order)

@bp.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    form = ClientForm()
    if form.validate_on_submit():
        try:
            client = Client(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                date_of_birth=form.date_of_birth.data,
                loyalty_points=form.loyalty_points.data,
                notes=form.notes.data
            )
            db.session.add(client)
            db.session.commit()
            
            log_security_event('client_created', f'Client created: {client.full_name}', user_id=current_user.id)
            
            flash(f'Client "{client.full_name}" has been added successfully!', 'success')
            return redirect(url_for('main.clients'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding client: {str(e)}', 'danger')
    
    return render_template('add_client.html', form=form)

@bp.route('/clients/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    form = ClientForm(obj=client)
    form._obj = client  # For email validation
    
    if form.validate_on_submit():
        try:
            form.populate_obj(client)
            client.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_security_event('client_updated', f'Client updated: {client.full_name}', user_id=current_user.id)
            
            flash(f'Client "{client.full_name}" has been updated successfully!', 'success')
            return redirect(url_for('main.clients'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating client: {str(e)}', 'danger')
    
    return render_template('edit_client.html', form=form, client=client)

@bp.route('/clients/delete/<int:client_id>', methods=['POST'])
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    client_name = client.full_name
    
    try:
        db.session.delete(client)
        db.session.commit()
        
        log_security_event('client_deleted', f'Client deleted: {client_name}', user_id=current_user.id)
        
        flash(f'Client "{client_name}" has been deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting client: {str(e)}', 'danger')
    
    return redirect(url_for('main.clients'))

# Employee routes
@bp.route('/employees')
@login_required
def employees():
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Insufficient permissions.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    search_form = SearchForm()
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Process search filters
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'full_name')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Sanitize and validate inputs
    query = sanitize_input(query)
    sort_field, sort_direction = parse_sort_param(sort_by, sort_order, 
                                                 allowed_fields=['username', 'full_name', 'email', 'department', 'role'])
    
    # Build query
    employees_query = Employee.query
    
    if query:
        employees_query = employees_query.filter(
            (Employee.username.ilike(f'%{query}%')) | 
            (Employee.full_name.ilike(f'%{query}%')) | 
            (Employee.email.ilike(f'%{query}%')) |
            (Employee.department.ilike(f'%{query}%'))
        )
    
    # Apply sorting
    if sort_direction == 'asc':
        employees_query = employees_query.order_by(getattr(Employee, sort_field).asc())
    else:
        employees_query = employees_query.order_by(getattr(Employee, sort_field).desc())
    
    # Paginate results
    pagination = employees_query.paginate(page=page, per_page=per_page, error_out=False)
    employee_list = pagination.items
    
    return render_template('employees.html', employees=employee_list, pagination=pagination, 
                           search_form=search_form, query=query, sort_by=sort_by, sort_order=sort_order)

@bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if current_user.role != 'admin':
        flash('Access denied. Insufficient permissions.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            employee = Employee(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                department=form.department.data,
                role=form.role.data
            )
            employee.set_password(form.password.data)
            db.session.add(employee)
            db.session.commit()
            
            log_security_event('employee_created', f'Employee created: {employee.full_name}', user_id=current_user.id)
            
            flash(f'Employee "{employee.full_name}" has been added successfully!', 'success')
            return redirect(url_for('main.employees'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'danger')
    
    return render_template('add_employee.html', form=form)

@bp.route('/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    if current_user.role != 'admin':
        flash('Access denied. Insufficient permissions.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    employee = Employee.query.get_or_404(employee_id)
    form = ProfileForm(obj=employee)
    
    if form.validate_on_submit():
        try:
            employee.full_name = form.full_name.data
            employee.email = form.email.data
            employee.department = form.department.data
            employee.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_security_event('employee_updated', f'Employee updated: {employee.full_name}', user_id=current_user.id)
            
            flash(f'Employee "{employee.full_name}" has been updated successfully!', 'success')
            return redirect(url_for('main.employees'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'danger')
    
    return render_template('edit_employee.html', form=form, employee=employee)

@bp.route('/employees/delete/<int:employee_id>', methods=['POST'])
@login_required
def delete_employee(employee_id):
    if current_user.role != 'admin':
        flash('Access denied. Insufficient permissions.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Prevent deleting yourself
    if employee.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('main.employees'))
    
    employee_name = employee.full_name
    
    try:
        db.session.delete(employee)
        db.session.commit()
        
        log_security_event('employee_deleted', f'Employee deleted: {employee_name}', user_id=current_user.id)
        
        flash(f'Employee "{employee_name}" has been deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'danger')
    
    return redirect(url_for('main.employees'))

# Profile routes

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            current_user.full_name = form.full_name.data
            current_user.email = form.email.data
            current_user.department = form.department.data
            current_user.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_security_event('profile_updated', f'Profile updated for {current_user.username}', user_id=current_user.id)
            
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('main.profile'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('profile.html', form=form)

@bp.route('/security_logs')
@login_required
def security_logs():
    if current_user.role != 'admin':
        flash('Access denied. Insufficient permissions.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    logs = SecurityLog.query.order_by(SecurityLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('security_logs.html', logs=logs)

# Error handlers
@bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
