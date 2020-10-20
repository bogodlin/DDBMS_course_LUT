from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, MultipleFileField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from eye_for_eye_optician.models import Optician, Citizen

# Optician Registration form

class RegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=200)])
    surname = StringField('Surname',
                          validators=[DataRequired(), Length(min=2, max=200)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        optician = Optician.query.filter_by(email=email.data).first()
        if optician:
            raise ValidationError('Email already taken')

# Optician Login form

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Password reset request form

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Optician.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

# Password change form

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# Optician Update form

class UpdateAccountForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    submit = SubmitField('Update')

# Case creation form

class OpticianUploadForm(FlaskForm):
    optician_comment = TextAreaField('Comment',
                            validators=[DataRequired()])
    files = MultipleFileField('File(s) uploads', validators=[DataRequired()])
    submit = SubmitField('Upload')

# Citizen Search form

class CitizenSearchForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Find')


# Citizen Registration form

class CitizenRegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=200)])
    surname = StringField('Surname',
                          validators=[DataRequired(), Length(min=2, max=200)])

    date_of_birth = DateField('Date of birth', format="%d/%m/%Y")

    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    phone_number = StringField('Phone number')

    #TODO Add country

    picture = FileField('Add Picture', validators=[FileAllowed(['jpg', 'png']), DataRequired()])

    submit = SubmitField('Register Citizen')

    def validate_email(self, email):
        citizen = Citizen.query.filter_by(email=email.data).first()
        if citizen:
            raise ValidationError('Email already taken. Enter another email.')



