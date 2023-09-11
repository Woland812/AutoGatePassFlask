from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from flask_paginate import get_page_args, Pagination, get_page_parameter

from models import LogCar, CarNumber

recognition_events = Blueprint('recognition_events', __name__)


@recognition_events.route('/recognition-events')
@login_required
def index():
    per_page = 50
    page = request.args.get(get_page_parameter(), type=int, default=1)
    if current_user.is_admin:
        total = LogCar.query.count()
        events = LogCar.query.order_by(LogCar.date.desc()).paginate(page=page, per_page=per_page)
    else:
        total = LogCar.query.join(CarNumber).filter_by(user_id=current_user.id).count()
        events = LogCar.query.join(CarNumber).filter_by(user_id=current_user.id).order_by(LogCar.date.desc()).paginate(page=page, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('recognition_events/index.html', events=events, pagination=pagination)
