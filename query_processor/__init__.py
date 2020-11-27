from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_mail import Mail

app = Flask(__name__)
app.config.from_json('qp_config.json')
db = SQLAlchemy(app)
mail = Mail(app)

from query_processor import routes



