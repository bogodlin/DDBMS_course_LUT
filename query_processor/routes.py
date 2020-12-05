from query_processor import app, mail
from flask import jsonify, request
import jwt
import requests
from functools import wraps
import os
from query_processor.models import *
from PIL import Image
from flask_mail import Message

class Token:
    token = jwt.encode({'hardware_id': app.config["ID"]}, app.config['SECRET_KEY'])

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

@app.route('/')
def home():
    return 'Welcome to the E4E platform'

# Opticians

@app.route('/register_optician', methods=["POST"])
@token_required
def register_optician():
    content = request.json
    token = request.headers['x-access-token']
    hardware_id = jwt.decode(token, app.config['SECRET_KEY'])['hardware_id']
    organisation = Organisation.query.filter_by(hardware_id=hardware_id).first()
    optician = Optician(name=content["name"], surname=content["surname"], email=content["email"],
                        password=content["password"], organisation=organisation.id)
    db.session.add(optician)
    db.session.commit()

    return jsonify({"created_id": optician.id})

# Ophtalmologists

@app.route('/register_ophtalmologist', methods=["POST"])
@token_required
def register_ophtalmologist():
    content = request.json
    token = request.headers['x-access-token']
    hardware_id = jwt.decode(token, app.config['SECRET_KEY'])['hardware_id']
    organisation = Organisation.query.filter_by(hardware_id=hardware_id).first()
    ophtalmologist = Ophtalmologist(name=content["name"], surname=content["surname"], email=content["email"],
                        password=content["password"], organisation=organisation.id)
    db.session.add(ophtalmologist)
    db.session.commit()

    return jsonify({"created_id": ophtalmologist.id})

# Cases

@app.route('/register_case', methods=["GET", "POST"])
@token_required
def register_case():
    headers = request.headers
    names = [name for name in request.files]
    filenames = []
    for file in names:
        content = request.files[file]
        content.save(os.path.join('query_processor/static/cases', content.filename))
        filenames.append(content.filename)

    selected_ophtalmologist = find_free_ophtalmologist()
    ophtalmologist_organisation_url = Organisation.query.filter_by(id=Ophtalmologist.query.filter_by(id=selected_ophtalmologist).first().organisation).first().service_url

    case = Case(citizen=int(headers['citizen']), code=headers['code'], optician=int(headers['optician']),
                ophtalmologist=selected_ophtalmologist,
                status=1, optician_comment=headers['optician_comment'],
                images=filenames)

    db.session.add(case)
    db.session.commit()

    files = {}
    for file in range(len(filenames)):
        files['file{}'.format(file)] = open('query_processor/static/cases/' + filenames[file], 'rb')

    try:
        requests.post(
            ophtalmologist_organisation_url + '/receive_new_case',
            headers={"x-access-token": Token.token,
                     "id": str(case.id),
                     "optician_comment": str(case.optician_comment),
                     "citizen": str(case.citizen),
                     "code": str(case.code),
                     "optician": str(case.optician),
                     "ophtalmologist": str(case.ophtalmologist),
                     "status": str(case.status)
                     },
            files=files
        ).json()

        # if request_to_ophta['message'] == 'Success':
        #     return 'Test'

        return jsonify({"case_id": case.id})

    except TypeError:
        return jsonify({'message' : 'Saving error!'})

def find_free_ophtalmologist():

    # TODO find ophto which hasn't got any assigned cases
    free_ophtalmologist_query = """
    select free_ophta.id, count(*) as "Cases"
    from "case" as "cases"
         right outer join
         (select * from "ophtalmologist" where active = True and available = True) "free_ophta"
         on cases.ophtalmologist = free_ophta.id
    group by free_ophta.id
    order by 2
    limit 1
    """
    free_ophtalmologist = db.engine.execute(free_ophtalmologist_query).first().id
    return free_ophtalmologist

@app.route("/case/<case_id>/reject", methods=['POST', 'GET'])
@token_required
def reject_case(case_id):
    content = request.json
    case = Case.query.get_or_404(case_id)
    citizen = Citizen.query.filter_by(id=case.citizen).first()
    send_result_email(citizen, case.code)
    case.status, case.ophtalmologist_comment = 2, content['ophtalmologist_comment']
    db.session.commit()

    return jsonify({'message': 'Success'})

@app.route("/case/<case_id>/accept", methods=['POST', 'GET'])
@token_required
def accept_case(case_id):
    content = request.json
    case = Case.query.get_or_404(case_id)
    citizen = Citizen.query.filter_by(id=case.citizen).first()
    send_result_email(citizen, case.code)
    case.status, case.ophtalmologist_comment = 3, content['ophtalmologist_comment']
    db.session.commit()

    return jsonify({'message': 'Success'})

def send_result_email(citizen,case_code):
    token = jwt.encode({'case_id': case_code}, str(app.config['SECRET_KEY'])).decode()
    msg = Message('Case results',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[citizen.email,app.config["DL_MAIL"]])
    msg.body = f'''The case has been checked.
To see the results, please, enter the following link:
{app.config["REG_HOST"] + '/' + 'view_case'+ '/' + str(case_code) + '/' + str(token)}
'''
    mail.send(msg)

# Citizens

@app.route('/find_citizen', methods=["GET"])
@token_required
def find_citizen():
    content = request.json
    citizen = Citizen.query.filter_by(email=content['email']).first()
    if citizen:
        citizen_dict = dict((col, getattr(citizen, col)) for col in citizen.__table__.columns.keys())
        # logging.info('Found citizen by {}'.format(content['email']))
        return jsonify(citizen_dict)
    else:
        # logging.info('Have not found citizen by {}'.format(content['email']))
        return jsonify({'message': 'Have not found the citizen. Please, register a new one'})

@app.route('/register_citizen', methods=["POST"])
@token_required
def register_citizen():
    headers = request.headers
    content = request.files['file']
    content.save(os.path.join('query_processor/static/citizens', content.filename))

    citizen = Citizen(name=headers["name"], surname=headers["surname"], email=headers["email"],
                        date_of_birth=headers["date_of_birth"], phone_number=headers["phone_number"],
                      image_file=content.filename, country=1) #TODO remove hardcoded country
    db.session.add(citizen)
    db.session.commit()

    return jsonify({"created_id": citizen.id})

@app.route("/change_ophta_availablity/<ophta_id>", methods=['POST', 'GET'])
@token_required
def change_ophta_availablity(ophta_id):
    content = request.json
    ophtalmologist = Ophtalmologist.query.get_or_404(ophta_id)
    ophtalmologist.available = content['availability']
    db.session.commit()

    return jsonify({'message': 'Success'})
