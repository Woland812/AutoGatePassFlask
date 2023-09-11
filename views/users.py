from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

import constants
from forms.user import CreateUserForm, EditUserForm
from helpers import admin_required, db
from models import User

users = Blueprint('users', __name__)


@users.route('/users')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('users/index.html', users=users)


@users.route('/users/view/<int:user_id>')
@login_required
@admin_required
def view(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/view.html', user=user)


@users.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        try:
            form.populate_obj(user)
            if form.password.data:
                user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            flash('Пользователь успешно отредактирован', 'success')
            return redirect(url_for('users.index'))
        except Exception as e:
            print(e)
            flash('Ошибка при редактировании пользователя', 'danger')
    return render_template('users/edit.html', user=user, form=form)


@users.route('/users/delete/<int:user_id>')
@login_required
@admin_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.type == constants.USER_TYPE_ADMIN:
        flash('Нельзя изменить удалить администратора', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('пользователя успешно удален', 'success')
    return redirect(url_for('users.index'))


@users.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = CreateUserForm()
    if form.validate_on_submit():
        try:
            new_user = User(username=form.username.data, type=2, password_hash=generate_password_hash(form.password.data),
                        full_name=form.full_name.data, address=form.address.data, phone_number=form.phone_number.data,
                        status=form.status.data, additional_info=form.additional_info.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Пользователь успешно добавлен', 'success')
            return redirect(url_for('users.index'))
        except Exception as e:
            print(e)
            flash('Ошибка при добавлении пользователя', 'danger')
            return render_template('users/create.html', form=form)
    print(form.errors)
    return render_template('users/create.html', form=form)


@users.route('/users/toggle_status/<int:user_id>')
@login_required
@admin_required
def toggle_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.type == constants.USER_TYPE_USER:
        user.status = not user.status
        db.session.commit()
        flash('Статус пользователя успешно изменен', 'success')
    else:
        flash('Нельзя изменить статус администратора', 'danger')
    return redirect(url_for('users.index'))
