from flask import Blueprint
from flask_login import login_required

profile = Blueprint('profile', __name__)

@profile.route('/profile')
@login_required
def index():

    return "Profile page"