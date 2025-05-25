from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
limiter = Limiter(key_func=lambda: "default")  # Will be initialized properly in main.py
talisman = Talisman()
csrf = CSRFProtect()
