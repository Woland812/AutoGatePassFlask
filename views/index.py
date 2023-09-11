from flask import Blueprint, redirect, url_for
from flask_login import current_user

from models import User

index = Blueprint('main', __name__)


@index.route('/')
def index_page():
    if current_user.is_authenticated:
        return redirect(url_for('recognition_events.index'))
    else:
        return redirect(url_for('auth.login'))
