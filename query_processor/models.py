from query_processor import db, app
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

class Citizen(db.Model):

    __tablename__ = 'citizen'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='citizen_default.png')
    cases = db.relationship('Case', backref='case_citizen', lazy=True)
    country = db.Column(db.Integer, db.ForeignKey('country.id'))

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))

class Optician(db.Model):

    __tablename__ = 'optician'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='optician_default.png')
    active = db.Column(db.Boolean, default=False)
    available = db.Column(db.Boolean, default=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))

    cases = db.relationship('Case', backref='case_optician', lazy=True)

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))


class Ophtalmologist(db.Model):

    __tablename__ = 'ophtalmologist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='ophtalmologist_default.png')
    # country = db.Column(db.Integer, db.ForeignKey('country.id'))
    cases = db.relationship('Case', backref='case_ophtalmologist', lazy=True)
    active = db.Column(db.Boolean, default=False)
    available = db.Column(db.Boolean, default=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))


class Status(db.Model):

    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    cases = db.relationship('Case', backref='casestatus', lazy=True)

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))

class Case(db.Model):

    __tablename__ = 'case'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    citizen = db.Column(db.Integer, db.ForeignKey('citizen.id'))
    optician = db.Column(db.Integer, db.ForeignKey('optician.id'))
    ophtalmologist = db.Column(db.Integer, db.ForeignKey('ophtalmologist.id'))
    status = db.Column(db.Integer, db.ForeignKey('status.id'))
    optician_comment = db.Column(db.String, nullable=True)
    ophtalmologist_comment = db.Column(db.String, nullable=True)
    images = db.Column(ARRAY(db.String))

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))

class Country(db.Model):
    __tablename__ = 'country'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    key = db.Column(db.String)
    citizens = db.relationship('Citizen', backref='citizen_status', lazy=True)

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))

class Organisation(db.Model):

    __tablename__ = 'organisation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    country = db.Column(db.Integer, db.ForeignKey('country.id'))
    hardware_id = db.Column(db.String, nullable=False)
    service_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))