from query_processor import app
from flask import jsonify, request, make_response
import jwt
import requests
import datetime
import json_parser
from functools import wraps
import os
from query_processor.models import *
from PIL import Image

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

@app.route('/')
def home():
    return 'Welcome to the E4E platform'

# Opticians

@app.route('/register_optician', methods=["POST"])
@token_required
def register_optician():
    content = request.json
    optician = Optician(name=content["name"], surname=content["surname"], email=content["email"],
                        password=content["password"])
    db.session.add(optician)
    db.session.commit()

    return jsonify({"created_id": optician.id})

# Ophtalmologists

@app.route('/register_ophtalmologist', methods=["POST"])
@token_required
def register_ophtalmologist():
    content = request.json
    ophtalmologist = Ophtalmologist(name=content["name"], surname=content["surname"], email=content["email"],
                        password=content["password"])
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

    case = Case(citizen=int(headers['citizen']), code=headers['code'], optician=int(headers['optician']),
                ophtalmologist=find_free_ophtalmologist(),
                status=1, optician_comment=headers['optician_comment'],
                images=filenames)

    db.session.add(case)
    db.session.commit()

    files = {}
    for file in range(len(filenames)):
        files['file{}'.format(file)] = open('query_processor/static/cases/' + filenames[file], 'rb')

    try:
        requests.post(
            str(json_parser.retrieve_host('ophtalmologist')) + str(json_parser.retrieve_port('ophtalmologist')) + '/receive_new_case',
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
         inner join
         (select * from "ophtalmologist" where active = True and available = True) "free_ophta"
         on cases.ophtalmologist = free_ophta.id
    group by free_ophta.id
    order by 2
    limit 1
    """
    free_ophtalmologist = db.engine.execute(free_ophtalmologist_query).first().id
    return free_ophtalmologist

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
                      image_file=content.filename)
    db.session.add(citizen)
    db.session.commit()

    return jsonify({"created_id": citizen.id})

@app.route('/test_log', methods=["GET"])
@token_required
def test_log():
    # logging.info('Have not found citizen by {}'.format(content['email']))

    return 'Log'