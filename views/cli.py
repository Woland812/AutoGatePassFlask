import click
from flask import Blueprint
from werkzeug.security import generate_password_hash

from helpers import db
from license_plate_recognition_demon import start_daemon, stop_daemon
from models import User, AdminSetting

cli = Blueprint('admin', __name__)


@cli.cli.command('create')
@click.argument('username')
def create(username):
    password = click.prompt('Пароль', hide_input=True, confirmation_prompt=True)
    hashed_password = generate_password_hash(password)

    admin = User(username=username, password_hash=hashed_password, type=1)
    db.session.add(admin)
    db.session.commit()

    print(f"Администратор {username} успешно создан.")


@cli.cli.command('init_db')
def init_db():
    db.create_all()
    print("База данных успешно создана.")


@cli.cli.command('init_settings')
def init_settings():
    gate_phone_input = input("Введите телефонный номер шлагбаума: ")
    api_key_input = input("Введите API ключ: ")
    campaign_id_input = input("Введите ID кампании в сервисе zvonok: ")
    camera_url_input = input("Введите URL камеры: ")
    api_key = AdminSetting.query.filter_by(key='zvonok_api_key').first()
    gate_phone = AdminSetting.query.filter_by(key='gate_phone').first()
    campaign_id = AdminSetting.query.filter_by(key='campaign_id').first()
    camera_url = AdminSetting.query.filter_by(key='camera_url').first()
    status_demon = AdminSetting.query.filter_by(key='status_demon').first()
    if not api_key:
        api_key = AdminSetting(key='zvonok_api_key', value=api_key_input)
        db.session.add(api_key)
    else:
        api_key.value = api_key_input

    if not gate_phone:
        gate_phone = AdminSetting(key='gate_phone', value=gate_phone_input)
        db.session.add(gate_phone)
    else:
        gate_phone.value = gate_phone_input

    if not campaign_id:
        campaign_id = AdminSetting(key='campaign_id', value=campaign_id_input)
        db.session.add(campaign_id)
    else:
        campaign_id.value = campaign_id_input

    if not camera_url:
        camera_url = AdminSetting(key='camera_url', value=camera_url_input)
        db.session.add(camera_url)
    else:
        camera_url.value = camera_url_input

    if not status_demon:
        status_demon = AdminSetting(key='status_demon', value='0')
        db.session.add(status_demon)

    db.session.commit()
    print("Настройки успешно добавлены/обновлены.")

@cli.cli.command('test')
def test():
    start_daemon()

@cli.cli.command('test2')
def test2():
    stop_daemon()