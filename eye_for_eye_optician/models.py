from eye_for_eye_optician import db, login_manager, app
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return Optician.query.get(int(user_id))

#TODO map to the columns added directly to db

class Citizen(db.Model):

    __tablename__ = 'citizen'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False)
    image_file = db.Column(db.String, nullable=False, default='citizen_default.png')
    cases = db.relationship('Case', backref='case_citizen', lazy=True)
    # country = db.Column(db.Integer, db.ForeignKey('country.id'))

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))

class Optician(db.Model, UserMixin):

    __tablename__ = 'optician'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String, nullable=False, default='optician_default.png')
    active = db.Column(db.Boolean, default=False)
    # country = db.Column(db.Integer, db.ForeignKey('country.id'))

    cases = db.relationship('Case', backref='case_optician', lazy=True)

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Optician.query.get(user_id)

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
    status = db.Column(db.Integer, db.ForeignKey('status.id'))
    optician_comment = db.Column(db.String, nullable=True)
    images = db.Column(ARRAY(db.String))

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, default=datetime.utcnow)
    citizen = db.Column(db.Integer, db.ForeignKey('citizen.id'))
    optician = db.Column(db.Integer, db.ForeignKey('optician.id'))