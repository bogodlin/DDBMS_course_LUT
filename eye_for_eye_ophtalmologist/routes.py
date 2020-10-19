import os
import secrets
from PIL import Image
from eye_for_eye_ophtalmologist import app, bcrypt, mail
from flask import render_template, flash, redirect, url_for, session, request
from eye_for_eye_ophtalmologist.forms import *
from eye_for_eye_ophtalmologist.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        assigned_active_cases = Case.query.filter_by(ophtalmologist=current_user.id)\
            .order_by(Case.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('home.html', created_cases=assigned_active_cases)

    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')


# --------------------------------------- Registration, Login, Logout ---------------------------------------

@app.route("/register_ophtalmologist", methods=['GET', 'POST'])
def register_ophtalmologist():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        ophtalmologist = Ophtalmologist(name=form.name.data, surname=form.surname.data, email=form.email.data,
                            password=hashed_password)
        db.session.add(ophtalmologist)
        db.session.commit()
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('login_ophtalmologist'))
    return render_template('register_ophtalmologist.html', title='Register', form=form)


@app.route("/login_ophtalmologist", methods=['GET', 'POST'])
def login_ophtalmologist():
    form = LoginForm()
    if form.validate_on_submit():
        ophtalmologist = Ophtalmologist.query.filter_by(email=form.email.data).first()
        if ophtalmologist:
            if ophtalmologist.active == True:
                if bcrypt.check_password_hash(ophtalmologist.password, form.password.data):
                    login_user(ophtalmologist, remember=form.remember.data)
                    return redirect(url_for('home'))
                else:
                    flash('Login Unsuccessful. Please check email and password', 'danger')
            else:
                flash('User has not been activated yet', 'danger')
        else:
            flash('No user with the submitted email was found. Please, check it again', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Ophtalmologist's account

def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # output_size = (125, 125)
    i = Image.open(form_picture)
    # i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

# View case

@app.route("/case/<case_code>", methods=['GET', 'POST'])
@login_required
def view_case(case_code):
    case = Case.query.filter_by(code=case_code).first()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('view_case.html', case=case)


# Reset password

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='Eye for eye',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Ophtalmologist.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login_ophtalmologist'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Ophtalmologist.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login_ophtalmologist'))
    return render_template('reset_token.html', title='Reset Password', form=form)