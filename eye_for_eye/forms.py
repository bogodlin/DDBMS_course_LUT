from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

# Case Check form

class CaseCheckForm(FlaskForm):
    case_code = StringField('Case code',
                        validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    submit = SubmitField('Search')




