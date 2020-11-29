import os
from eye_for_eye import app
from flask import render_template, flash, redirect, url_for, session, request
from eye_for_eye.forms import *
from eye_for_eye.models import Case, Citizen
import jwt


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = CaseCheckForm()
    sidebar_form = AppointmentForm()
    if form.validate_on_submit():
        case = Case.query.filter_by(code=form.case_code.data).first()
        if case:
            citizen = Citizen.query.filter_by(id=case.citizen).first()
            if citizen.surname == form.surname.data:
                token = jwt.encode({'case_id': case.code}, str(app.config['SECRET_KEY']))
                return redirect(url_for('view_case', case_code=case.code, token=token))
            else:
                flash(f'Please, check the surname field once again', 'danger')
        else:
            flash(f'No case with {form.case_code.data} is found', 'danger')
    return render_template('home.html', form=form, sidebar_form=sidebar_form)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/view_case/<case_code>/<token>", methods=['GET', 'POST'])
def view_case(case_code, token):
    try:
        jwt.decode(token, str(app.config['SECRET_KEY']))
        case = Case.query.filter_by(code=case_code).first()
        citizen = Citizen.query.filter_by(id=case.citizen).first()
        return render_template('view_case.html', case=case, citizen=citizen)

    except Exception:
        flash('Authentication failed', 'danger')
        return redirect(url_for("home"))
