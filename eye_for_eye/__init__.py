from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from applications_logs_setup import logsetup

app = Flask(__name__)
app.config.from_json('reg_config.json')
db = SQLAlchemy(app)

logsetup(app, app.name)

from eye_for_eye import routes

