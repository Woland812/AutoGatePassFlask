from flask import Blueprint, session, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from forms.car_numbers import CreateCarNumberForm
from helpers import admin_required, db
from models import User, CarNumber

car_numbers = Blueprint('car_numbers', __name__)

type_mapping = {
    1: 'Постоянный',
    2: 'Временный',
    3: 'Разовый'}


@car_numbers.route('/car-numbers')
@login_required
def index():
    if not current_user.is_admin:
        cars_number = CarNumber.query.filter_by(user_id=current_user.id).all()
    else:
        cars_number = CarNumber.query.all()
    return render_template('car_numbers/index.html', cars_number=cars_number, type_mapping=type_mapping)


@car_numbers.route('/car-numbers/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateCarNumberForm()
    if current_user.is_admin:
        users = User.query.all()
        form.user_id.choices = [(user.id, user.username) for user in users]
    else:
        form.user_id.choices = (current_user.id, current_user.username)
    if form.validate_on_submit():
        try:
            car_number = CarNumber(
                car_number=form.car_number.data.upper(),
                car_info=form.car_info.data,
                status=form.status.data,
                user_id=form.user_id.data if current_user.is_admin else current_user.id,
                date_start=form.date_start.data,
                date_end=form.date_end.data,
                type=form.type.data
            )
            db.session.add(car_number)
            db.session.commit()
            flash('Разрешенный номер машины успешно добавлен', 'success')
            return redirect(url_for('car_numbers.index'))
        except Exception as e:
            print(e)
            flash('Ошибка при добавлении разрешенного номера машины', 'danger')
    else:
        print(form.errors)

    return render_template('car_numbers/create.html', form=form)


@car_numbers.route('/car-numbers/edit/<int:number_id>', methods=['GET', 'POST'])
@login_required
def edit(number_id):
    car_number = CarNumber.query.get_or_404(number_id)
    if not current_user.is_admin and car_number.user_id != current_user.id:
        flash('У вас нет прав для редактирования этого номера машины', 'danger')
        return redirect(url_for('car_numbers.index'))
    form = CreateCarNumberForm(obj=car_number)
    users = User.query.all()
    form.user_id.choices = [(user.id, user.username) for user in users]
    if form.validate_on_submit():
        try:
            form.populate_obj(car_number)
            db.session.commit()
            flash('Номер машины успешно отредактирован', 'success')
            return redirect(url_for('car_numbers.index'))
        except Exception as e:
            print(e)
            flash('Ошибка при редактировании номера машины', 'danger')
    else:
        print(form.errors)
    return render_template('car_numbers/edit.html', form=form, car_number=car_number)


@car_numbers.route('/car-numbers/delete/<int:number_id>')
@login_required
def delete(number_id):
    car_number = CarNumber.query.get_or_404(number_id)
    if not current_user.is_admin or car_number.user_id != current_user.id:
        flash('У вас нет прав для удаления этого номера машины', 'danger')
    else:
        try:
            db.session.delete(car_number)
            db.session.commit()
            flash('Номер машины успешно удален', 'success')
        except Exception as e:
            print(e)
            flash('Ошибка при удалении номера машины', 'danger')
    return redirect(url_for('car_numbers.index'))


@car_numbers.route('/car-numbers/view/<int:number_id>')
@login_required
def view(number_id):
    car_number = CarNumber.query.get_or_404(number_id)
    if not current_user.is_admin or car_number.user_id != current_user.id:
        flash('У вас нет прав для просмотра этого номера машины', 'danger')
        return redirect(url_for('car_numbers.index'))
    return render_template('car_numbers/view.html', car_number=car_number, type=type_mapping[car_number.type])


@car_numbers.route('/car-numbers/toggle_status/<int:number_id>')
@login_required
@admin_required
def toggle_status(number_id):
    car_number = CarNumber.query.get_or_404(number_id)
    try:
        car_number.status = not car_number.status
        db.session.commit()
        flash('Статус номера машины успешно изменен', 'success')
    except Exception as e:
        print(e)
        flash('Ошибка при изменении статуса номера машины', 'danger')
    return redirect(url_for('car_numbers.index'))
