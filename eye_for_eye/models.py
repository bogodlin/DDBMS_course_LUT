from eye_for_eye import db, app
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class Citizen(db.Model, UserMixin):

    __tablename__ = 'citizen'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False)
    image_file = db.Column(db.String, nullable=False, default='citizen_default.png')
    cases = db.relationship('Case', backref='case_citizen', lazy=True)
    country = db.Column(db.Integer, db.ForeignKey('country.id'))

    def __repr__(self):
        return str(dict((col, getattr(self, col)) for col in self.__table__.columns.keys()))

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
        return Citizen.query.get(user_id)

class Case(db.Model):

    tablename = 'case'

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
