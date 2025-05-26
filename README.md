# ClientShield- Shielding Personal Info from Cyber Attacks

A secure, full-featured web application for supermarket operations management with advanced cybersecurity protection.

## 🚀 Project Overview

ClientShield is a Flask-based web application designed to streamline supermarket operations through digital transformation. The system provides secure role-based access control, real-time inventory management, comprehensive client database management, and employee administration with robust cybersecurity protocols.

## ✨ Key Features

### 🔐 Security Features
- **XSS Prevention**: Real-time input sanitization and pattern detection
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CSRF Protection**: Token-based form validation
- **Secure Authentication**: Password hashing with role-based access control
- **Security Logging**: Comprehensive audit trails and event monitoring
- **Session Management**: Encrypted cookies with automatic timeout

### 📊 Core Functionality
- **Inventory Management**: Complete CRUD operations with stock tracking
- **Client Management**: Customer database with loyalty points system
- **Employee Administration**: Staff management with role assignments
- **Real-time Dashboard**: Role-specific interfaces with live data
- **Search & Filter**: Advanced search capabilities across all modules
- **Responsive Design**: Mobile-friendly Bootstrap interface

## 🛠️ Technology Stack

- **Backend**: Python Flask with MVC architecture
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, JavaScript, Jinja2 templates
- **Security**: Flask-Login, WTForms, custom security utilities

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL or MySQL database
- Git

## ⚡ Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/supermart-pro.git
   cd supermart-pro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "SESSION_SECRET=your-secret-key-here" > .env
   echo "DATABASE_URL=postgresql://user:password@localhost:5432/supermart_db" >> .env
   ```

4. **Initialize database**
   ```bash
   python main.py
   ```

5. **Run the application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Default admin credentials will be created automatically

## 🗄️ Database Configuration
### MySQL Setup
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE supermart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Set environment variable
export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/supermart_db"
```

## 👥 User Roles

- **Admin**: Full system access, user management, security logs
- **Manager**: Inventory and client management, employee oversight
- **Employee**: Basic inventory operations, client interactions

## 🔒 Security Implementation

### XSS Prevention
- Real-time input validation in `static/js/security.js`
- Pattern detection for malicious scripts
- Automatic content sanitization

### SQL Injection Protection
- SQLAlchemy ORM with parameterized queries
- Input validation and sanitization utilities
- No raw SQL execution

### CSRF Protection
- Token-based validation on all forms
- Cross-origin request blocking
- Automatic token generation and validation

## 📁 Project Structure

```
supermart-pro/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── models.py              # Database models
├── routes.py              # Application routes
├── forms.py               # WTForms definitions
├── utils.py               # Utility functions
├── extensions.py          # Flask extensions
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── inventory.html
│   ├── clients.html
│   └── employees.html
├── static/
│   ├── css/
│   │   └── custom.css
│   └── js/
│       ├── main.js
│       └── security.js
└── requirements.txt
```

## 🧪 Testing

The application includes comprehensive testing for:
- User authentication and authorization
- CRUD operations for all modules
- Security vulnerability assessments
- Form validation and error handling

## 🚀 Deployment

### Production Deployment
1. Set environment variables for production
2. Configure secure database connection
3. Enable HTTPS and security headers
4. Set up monitoring and logging

## 🔧 Configuration Options

### Environment Variables
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Environment mode (development/production)

### Security Settings
- CSRF token expiration: 1 hour
- Session timeout: 30 minutes
- Password minimum length: 8 characters
- Failed login attempt limit: 5 attempts

## 📈 Future Enhancements

- Mobile application development
- Advanced analytics dashboard
- Machine learning integration for demand forecasting
- Barcode scanning functionality
- Multi-branch support
- API development for third-party integrations

## 👨‍💻 Development Team

- **Naivaidhya Garg** - Database Design & Client Management
- **Devank Joshi** - Inventory System & Authentication
