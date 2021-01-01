from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_mail import Mail
from applications_logs_setup import logsetup


app = Flask(__name__)
app.config.from_json('qp_config.json')
db = SQLAlchemy(app)
mail = Mail(app)

logsetup(app, app.name)

# from .commands import create_tables

# app.cli.add_command(create_tables)

from query_processor import routes
