from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField


class AdminSettingsForm(FlaskForm):
    zvonok_api_key = StringField('Zvonok.com API KEY')
    gate_phone = StringField('Номер телефона шлагбаума')
    campaign_id = StringField('ID кампании')
    camera_url = StringField('URL камеры')
    status_demon = BooleanField('Статус демона', false_values=('0', 'False', False), default=False)
    submit = SubmitField('Сохранить')