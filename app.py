from flask import Flask

from views.admin_settings import admin_settings
from views.auth import auth
from views.car_numbers import car_numbers
from views.index import index
from views.cli import cli
from helpers import db, login_manager
import config
from views.recognition_events import recognition_events
from views.users import users

app = Flask(__name__, static_folder='static')
app.config.from_object(config.DevelopmentConfig)
db.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(index)
app.register_blueprint(users)
app.register_blueprint(car_numbers)
app.register_blueprint(admin_settings)
app.register_blueprint(recognition_events)
app.register_blueprint(cli)

login_manager.init_app(app)
login_manager.login_view = 'auth.login'

if __name__ == '__main__':
    app.run(port=8001, debug=True)
