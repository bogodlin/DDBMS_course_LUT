from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField


# Case Check form

class CaseCheckForm(FlaskForm):
    case_code = StringField('Case code',
                            validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    submit = SubmitField('Search')


class AppointmentForm(FlaskForm):
    # case_code = StringField('Case code',
    #                     validators=[DataRequired()])
    # surname = StringField('Surname', validators=[DataRequired()])
    # submit = SubmitField('Search')
    time = SelectField('Prefered time', choices=([1, '11:00 - 11:30'], [2, '12:00 - 12:30'], [3, '12:30 - 13:30']))
    date = DateField('Prefered date')
