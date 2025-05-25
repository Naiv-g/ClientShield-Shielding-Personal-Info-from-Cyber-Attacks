from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, FloatField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError
from models import Employee, Client
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    department = StringField('Department', validators=[Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    role = SelectField('Role', choices=[('employee', 'Employee'), ('manager', 'Manager'), ('admin', 'Administrator')])
    
    def validate_username(self, username):
        user = Employee.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = Employee.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class InventoryForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    category = SelectField('Category', choices=[
        ('grocery', 'Grocery'),
        ('dairy', 'Dairy'),
        ('meat', 'Meat & Poultry'),
        ('produce', 'Produce'),
        ('bakery', 'Bakery'),
        ('beverages', 'Beverages'),
        ('frozen', 'Frozen'),
        ('household', 'Household'),
        ('personal_care', 'Personal Care'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    supplier = StringField('Supplier', validators=[Length(max=100)])
    barcode = StringField('Barcode', validators=[Length(max=30)])

class ClientForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone', validators=[Length(max=20)])
    address = StringField('Address', validators=[Length(max=200)])
    city = StringField('City', validators=[Length(max=50)])
    state = StringField('State', validators=[Length(max=50)])
    postal_code = StringField('Postal Code', validators=[Length(max=20)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    loyalty_points = IntegerField('Loyalty Points', validators=[NumberRange(min=0)], default=0)
    notes = TextAreaField('Notes')
    
    def validate_email(self, email):
        # Allow updating existing client's email
        client = Client.query.filter_by(email=email.data).first()
        if client and hasattr(self, '_obj') and client.id != getattr(self._obj, 'id', None):
            raise ValidationError('Email already registered to another client.')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Length(max=100)])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    
    def validate_confirm_password(self, confirm_password):
        if confirm_password.data != self.new_password.data:
            raise ValidationError('Passwords do not match.')



class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    department = StringField('Department', validators=[Length(max=50)])
    
    def validate_email(self, email):
        from flask_login import current_user
        user = Employee.query.filter_by(email=email.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Email already in use by another employee.')
