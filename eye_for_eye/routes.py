import os
from eye_for_eye import app
from flask import render_template, flash, redirect, url_for, session, request
from eye_for_eye.forms import *
from eye_for_eye.models import Case


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = CaseCheckForm()
    if form.validate_on_submit():
        case = Case.query.filter_by(code=form.case_code.data).first()
        if case:
            return redirect(url_for('view_case', case_code=case.code))
        else:
            flash(f'No case with {form.case_code.data} is found', 'danger')
    return render_template('home.html', form = form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/view_case/<case_code>", methods=['GET', 'POST'])
def view_case(case_code):
    case = Case.query.filter_by(code=case_code).first()
    return render_template('view_case.html', case=case)
