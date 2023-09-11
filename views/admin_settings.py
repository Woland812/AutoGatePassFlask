import cv2
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, Response
from flask_login import login_required

from open_gate import open_gate
from forms.admin_settings import AdminSettingsForm
from helpers import admin_required, db
from license_plate_recognition_demon import start_daemon, stop_daemon
from models import AdminSetting

admin_settings = Blueprint('admin_settings', __name__)


@admin_settings.route('/admin-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    settings = AdminSetting.query.all()
    data = {}
    for setting in settings:
        data[setting.key] = setting.value
        if setting.key == 'status_demon':
            if setting.value == '1':
                data[setting.key] = True
            else:
                data[setting.key] = False
    form = AdminSettingsForm(data=data)
    if form.validate_on_submit():
        try:
            for key, value in form.data.items():
                setting = AdminSetting.query.filter_by(key=key).first()
                if setting:
                    setting.value = value
            db.session.commit()
            flash('Настройки успешно сохранены', 'success')

            if form.data['status_demon']:
                start_daemon()
            else:
                stop_daemon()

            return redirect(url_for('admin_settings.index'))
        except Exception as e:
            print(e)
            flash('Ошибка при сохранении настроек', 'danger')
    else:
        print(form.errors)
    return render_template('admin_settings/index.html', form=form)


@admin_settings.route('/admin-settings/test-api-key')
@login_required
@admin_required
def test_api_key():
    api_call = open_gate()
    return jsonify(api_call['message'])


@admin_settings.route('/admin-settings/video')
@login_required
@admin_required
def video():
    camera_url = AdminSetting.query.filter_by(key='camera_url').first().value
    return Response(generate_frames(camera_url), mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_frames(camera_url):
    cap = cv2.VideoCapture(camera_url)

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@admin_settings.route('/admin-settings/toggle-daemon')
@login_required
@admin_required
def toggle_daemon():
    demon_status = AdminSetting.query.filter_by(key='status_demon').first()
    if demon_status.value == '0':
        demon_status.value = '1'
    else:
        demon_status.value = '0'

    db.session.commit()
    return redirect(url_for('admin_settings.index'))
