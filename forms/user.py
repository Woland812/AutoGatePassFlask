from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from models import User

class Unique(object):
    def __init__(self, message=None):
        if not message:
            message = u'Пользователь с таким именем уже существует.'
        self.message = message

    def __call__(self, form, field):
        if field.object_data == field.data:
            return
        check = User.query.filter_by(username=field.data).first()
        if check:
            raise ValidationError(self.message)

class CreateUserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=20), Unique()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    full_name = StringField('ФИО', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    status = SelectField('Статус', choices=[('1', 'Активный'), ('0', 'Заблокированный')],
                         validators=[DataRequired()])
    additional_info = TextAreaField('Дополнительная информация')
    submit = SubmitField('Добавить')

    def validate_username(self, field):
        existing_user = User.query.filter_by(username=field.data).first()
        if existing_user:
            raise ValidationError('Пользователь с таким именем уже существует.')


class EditUserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=20), Unique()])
    password = PasswordField('Пароль', default='')
    full_name = StringField('ФИО', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    status = SelectField('Статус', choices=[('1', 'Активный'), ('0', 'Заблокированный')],
                         validators=[DataRequired()])
    additional_info = TextAreaField('Дополнительная информация')
    submit = SubmitField('Сохранить изменения')

