import re
from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField,  SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, ValidationError, Optional


class CreateCarNumberForm(FlaskForm):
    car_number = StringField('Номер', validators=[DataRequired(), Length(min=8, max=9)])
    user_id = SelectField('Пользователь', coerce=int, validators=[DataRequired()])
    type = SelectField('Тип',
                       choices=[('1', 'Постоянный'), ('2', 'Временный'), ('3', 'Разовый')],
                       validators=[DataRequired()],
                       default='1')
    status = SelectField('Статус', choices=[('1', 'Активный'), ('0', 'Заблокированный')],
                         validators=[DataRequired()], default='1')
    car_info = StringField('Марка/модель и прочая доп. информация')
    date_start = DateField('Дата начала действия', validators=[DataRequired()], default=date.today)
    date_end = DateField('Дата окончания действия', validators=[Optional()])
    submit = SubmitField('Добавить')

    def validate_car_number(self, car_number):
        car_number = car_number.data
        if len(car_number) < 8 or len(car_number) > 9:
            raise ValidationError('Номер должен быть в формате: А123АА123')
        if not car_number[0].isalpha() or not car_number[1].isdigit() or not car_number[2].isdigit() or not \
                car_number[3].isdigit() or not car_number[4].isalpha() or not car_number[5].isalpha() or not \
                car_number[6].isdigit() or not car_number[7].isdigit() or (len(car_number) == 9 and not car_number[8].isdigit()):
            raise ValidationError('Номер должен быть в формате: А123АА123')
        # проверка определенных символов ABCEHKMOPTXY0123456789 регулярным выражением
        if not re.match(r'^[ABCEHKMOPTXY0123456789]+$', car_number):
            raise ValidationError('Номер должен содержать только буквы (ABCEHKMOPTXY) и цифры от 0 до 9')
        # проверка уникальности номера
        from models import CarNumber
        car_number = CarNumber.query.filter_by(car_number=car_number).first()

