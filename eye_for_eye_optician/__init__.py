from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os
from applications_logs_setup import logsetup

app = Flask(__name__)
app.config.from_json('opti_config.json')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)

logsetup(app, app.name)

from eye_for_eye_optician import routes

