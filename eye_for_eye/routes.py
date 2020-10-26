import os
from eye_for_eye import app
from flask import render_template, flash, redirect, url_for, session, request
from eye_for_eye.forms import *
from eye_for_eye.models import *


@app.route("/")
@app.route("/home")
def home():
    form = CaseCheckForm()
    return render_template('home.html', form = form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


