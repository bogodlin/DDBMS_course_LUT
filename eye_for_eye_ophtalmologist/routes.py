from PIL import Image
from eye_for_eye_ophtalmologist import app, bcrypt, mail, db
from flask import render_template, flash, redirect, url_for, session, request, jsonify
from eye_for_eye_ophtalmologist.forms import *
from eye_for_eye_ophtalmologist.models import Ophtalmologist, Case
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import requests, json_parser, os, secrets, jwt
from functools import wraps

class Token:
    token = jwt.encode({'hardware_id': str(os.getenv('HARDWARE_ID'))}, str(app.config['SECRET_KEY']))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        assigned_active_cases = Case.query.filter_by(ophtalmologist=current_user.id, status=1) \
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

        try:
            request = requests.post(
                str(json_parser.retrieve_host('qp')) + str(json_parser.retrieve_port('qp')) + '/register_ophtalmologist',
                headers={"x-access-token": Token.token},
                json={"name": form.name.data,
                      "surname": form.surname.data,
                      "email": form.email.data,
                      "password": hashed_password}).json()

            optician = Ophtalmologist(id=request["created_id"], name=form.name.data, surname=form.surname.data,
                                email=form.email.data,
                                password=hashed_password)

            db.session.add(optician)
            db.session.commit()
            flash(f'Account created for {form.email.data}!', 'success')
            return redirect(url_for('login_ophtalmologist'))

        except KeyError:
            return request

    return render_template('register_ophtalmologist.html', title='Register as Ophtalmologist', form=form)

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

# Receive case from platform

@app.route("/receive_new_case", methods=['GET', 'POST'])
def receive_new_case():
    print('Initiated')
    headers = request.headers
    names = [name for name in request.files]
    filenames = []
    for file in names:
        content = request.files[file]
        content.save(os.path.join('eye_for_eye_ophtalmologist/static/cases', content.filename))
        filenames.append(content.filename)

    case = Case(id=int(headers['id']), code=headers['code'],
                ophtalmologist=int(headers['ophtalmologist']),
                status=int(headers['status']), optician_comment=headers['optician_comment'],
                images=filenames)

    db.session.add(case)
    db.session.commit()

    return jsonify({'message': 'Success'})

# View case

@app.route("/case/<case_code>", methods=['GET', 'POST'])
@login_required
def view_case(case_code):
    form = CaseCommentForm()
    case = Case.query.filter_by(code=case_code).first()
    # image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if form.validate_on_submit():
        session['ophtalmologist_comment'] = form.ophtalmologist_comment.data
        if form.reject_case.data:
            return redirect(url_for('reject_case', case_id=case.id))
        elif form.accept_case.data:
            return redirect(url_for('accept_case', case_id=case.id))

    return render_template('view_case.html', form=form, case=case)


# Reject case

@app.route("/case/<case_id>/reject", methods=['POST', 'GET'])
@login_required
def reject_case(case_id):
    ophtalmologist_comment = session.get('ophtalmologist_comment', None)
    case = Case.query.get_or_404(case_id)

    try:
        request = requests.post(
            str(json_parser.retrieve_host('qp')) + str(json_parser.retrieve_port('qp')) + '/case/' + str(case.id) + '/reject',
            headers={"x-access-token": Token.token},
            json={"ophtalmologist_comment": case.ophtalmologist_comment}).json()

        case.status, case.ophtalmologist_comment = 2, ophtalmologist_comment

        db.session.commit()
        flash(f'Case {case.code} was rejected', 'warning')
        return redirect(url_for('home'))

    except KeyError:
        return request


# Accept case

@app.route("/case/<case_id>/accept", methods=['POST', 'GET'])
@login_required
def accept_case(case_id):
    ophtalmologist_comment = session.get('ophtalmologist_comment', None)
    case = Case.query.get_or_404(case_id)

    try:
        request = requests.post(
            str(json_parser.retrieve_host('qp')) + str(json_parser.retrieve_port('qp')) + '/case/' + str(
                case.id) + '/accept',
            headers={"x-access-token": Token.token},
            json={"ophtalmologist_comment": case.ophtalmologist_comment}).json()

        case.status, case.ophtalmologist_comment = 3, ophtalmologist_comment

        db.session.commit()
        flash(f'Case {case.code} was accepted', 'success')
        return redirect(url_for('home'))

    except KeyError:
        return request


# Reset password

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f'''Ophtalmologist intranet.
To reset your password, visit the following link:
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
