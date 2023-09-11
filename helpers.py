from functools import wraps

from flask import current_app
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)

    return decorated_function
