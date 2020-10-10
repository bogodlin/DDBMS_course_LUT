from eye_for_eye import db, login_manager
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Optician.query.get(int(user_id))

class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False)
    cases = db.relationship('Case', backref='case_citizen', lazy=True)

    def __repr__(self):
        return f"Citizen('{self.name}')"

class Optician(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    cases = db.relationship('Case', backref='case_optician', lazy=True)

    def __repr__(self):
        return f"Citizen('{self.name}')"

class Ophtalmologist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    cases = db.relationship('Case', backref='case_ophtalmologist', lazy=True)

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    cases = db.relationship('Case', backref='casestatus', lazy=True)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    citizen = db.Column(db.Integer, db.ForeignKey('citizen.id'))
    optician = db.Column(db.Integer, db.ForeignKey('optician.id'))
    ophtalmologist = db.Column(db.Integer, db.ForeignKey('ophtalmologist.id'))
    status = db.Column(db.Integer, db.ForeignKey('status.id'))
    comment = db.Column(db.String(120), nullable=True)
    images = db.Column(ARRAY(db.String))