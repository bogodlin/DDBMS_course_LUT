from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_mail import Mail

app = Flask(__name__)
app.config.from_json('qp_config.json')
db = SQLAlchemy(app)
mail = Mail(app)

# from .commands import create_tables

# app.cli.add_command(create_tables)

from query_processor import routes
