from eye_for_eye import app, bcrypt
from flask import render_template,flash, redirect, url_for
from eye_for_eye.forms import RegistrationForm, LoginForm, CitizenSearchForm
from eye_for_eye.models import *
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register_optician", methods=['GET', 'POST'])
def register_optician():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        optician = Optician(name=form.name.data, surname=form.surname.data, email=form.email.data, password=hashed_password)
        db.session.add(optician)
        db.session.commit()
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('login_optician'))
    return render_template('register_optician.html', title='Register', form=form)


@app.route("/login_optician", methods=['GET', 'POST'])
def login_optician():
    form = LoginForm()
    if form.validate_on_submit():
        optician = Optician.query.filter_by(email = form.email.data).first()
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

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/create_case', methods=['GET', 'POST'])
@login_required
def step1():
    form = CitizenSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('step2'))
    return render_template('step1.html', form=form)

@app.route('/step2')
@login_required
def step2():
    return render_template('step2.html')
