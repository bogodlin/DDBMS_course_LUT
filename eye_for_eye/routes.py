import os
import secrets
from PIL import Image
from eye_for_eye import app, bcrypt
from flask import render_template, flash, redirect, url_for, session, request
from eye_for_eye.forms import *
from eye_for_eye.models import *
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        created_cases = Case.query.filter_by(optician=current_user.id)
        return render_template('home.html', created_cases=created_cases)

    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


# --------------------------------------- Registration, Login, Logout ---------------------------------------

@app.route("/register_optician", methods=['GET', 'POST'])
def register_optician():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        optician = Optician(name=form.name.data, surname=form.surname.data, email=form.email.data,
                            password=hashed_password)
        db.session.add(optician)
        db.session.commit()
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('login_optician'))
    return render_template('register_optician.html', title='Register', form=form)


@app.route("/login_optician", methods=['GET', 'POST'])
def login_optician():
    form = LoginForm()
    if form.validate_on_submit():
        optician = Optician.query.filter_by(email=form.email.data).first()
        if optician and bcrypt.check_password_hash(optician.password, form.password.data):
            login_user(optician, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# --------------------------------------- Case creation ---------------------------------------

@app.route('/create_case', methods=['GET', 'POST'])
@login_required
def step1():
    form = CitizenSearchForm()
    if form.validate_on_submit():
        citizen = Citizen.query.filter_by(email=form.email.data).first()
        if citizen:
            # TODO Check for possible conflicts
            session['citizen_id'] = citizen.id
            return redirect(url_for('step2'))
        else:
            em = form.email.data
            form.email.data = ''
            flash(f'No registered citizen with {em} email address is found', 'danger')
    return render_template('step1.html', form=form)


@app.route('/step2', methods=['GET', 'POST'])
@login_required
def step2():
    form = OpticianUploadForm()
    found_citizen = session.get('citizen_id', None)
    citizen = Citizen.query.filter_by(id=found_citizen).first()
    image_file = url_for('static', filename='profile_pics/' + citizen.image_file)

    if form.validate_on_submit():
        files_filenames = []
        for file in form.files.data:
            picture_file = save_picture(file)
            files_filenames.append(picture_file)
        case = Case(citizen=found_citizen, optician=current_user.id, status=1, comment=form.comment.data,
                    images=files_filenames)
        db.session.add(case)
        db.session.commit()
        return render_template('case_created.html')

    return render_template('step2.html', image_file=image_file, citizen=citizen, form=form)


@app.route("/register_new_citizen", methods=['GET', 'POST'])
@login_required
def register_new_citizen():
    form = CitizenRegistrationForm()
    if form.validate_on_submit():
        # if form.picture.data:
        #     picture_file = save_picture(form.picture.data)
        # TODO add citizen photo setting

        new_citizen = Citizen(name=form.name.data, surname=form.surname.data, date_of_birth=form.date_of_birth.data,
                              email=form.email.data, phone_number=form.phone_number.data)

        db.session.add(new_citizen)
        db.session.commit()
        flash('New citizen has been created!', 'success')
        return redirect(url_for('step2'))

    return render_template('citizen_registration.html', title='Citizen', form=form)


# --------------------------------------- Optician's account ---------------------------------------

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
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
