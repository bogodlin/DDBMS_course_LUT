from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
#TODO deal with SQLALCHEMY_DATABASE_URI env variable
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost:5432/app"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from eye_for_eye import routes

