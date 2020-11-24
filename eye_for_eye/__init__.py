from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_json('reg_config.json')
db = SQLAlchemy(app)

from eye_for_eye import routes

