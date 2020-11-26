from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_json('qp_config.json')
db = SQLAlchemy(app)

from query_processor import routes



