from re import sub

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash
from flask_login import LoginManager, UserMixin

from helpers import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    type = db.Column(db.Integer, nullable=False, default=2)
    full_name = db.Column(db.String(128))
    address = db.Column(db.String(256))
    _phone_number = db.Column("phone_number", db.String(20))
    status = db.Column(db.Integer)
    additional_info = db.Column(db.Text)

    @property
    def is_admin(self):
        return self.type == 1

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @hybrid_property
    def phone_number(self):
        return f'+{self._phone_number[:1]} ({self._phone_number[1:4]}) {self._phone_number[4:7]}-{self._phone_number[7:]}' if self._phone_number else ''

    @phone_number.setter
    def phone_number(self, value):
        self._phone_number = sub(r'[^0-9]', '', value)


class CarNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_number = db.Column(db.String(15), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Integer, nullable=False, default=1)
    car_info = db.Column(db.String(256))
    date_start = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)
    user = db.relationship('User', backref='car_numbers')
    total_entries = db.Column(db.Integer, nullable=False, default=0)


class LogCar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_number_id = db.Column(db.Integer, db.ForeignKey('car_number.id'), nullable=False)
    car_number = db.relationship('CarNumber', backref='log_entries')
    date = db.Column(db.DateTime, nullable=False)
    hash_name = db.Column(db.String(16), nullable=False)


class AdminSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False)
    value = db.Column(db.String(256), nullable=False)
