from flask import Blueprint, session, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required

from forms.login import LoginForm
from models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('user'):
        return redirect(url_for('recognition_events.index'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('recognition_events.index'))
            else:
                flash('Неверное имя пользователя или пароль', 'danger')
        return render_template('auth/login.html', form=form)



# @auth.post('/login')
# def login_post():
#     username = request.form.get('username')
#     password = request.form.get('password')
#
#     # проверяем, что былли введены данные
#     if not username or not password:
#         return redirect(url_for('auth.login'))
#
#     # проверяем, что пользователь существует и пароль совпадает
#     user = User.query.filter_by(username=username).first()
#     if not user or not user.check_password(password):
#         return redirect(url_for('auth.login'))
#
#     # если все хорошо, то авторизуем пользователя
#     login_user(user)
#     return redirect(url_for('recognition_events.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
