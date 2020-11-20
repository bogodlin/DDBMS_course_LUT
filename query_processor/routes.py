from query_processor import app
from flask import jsonify, request, make_response
import jwt
import requests
import datetime
from functools import wraps
import os
from query_processor.models import *

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

# @app.route('/get_case/<case_id>', methods=["GET"])
# @token_required
# def get_case(case_id):
#     case = Case.query.filter_by(id=case_id).first()
#
#     case_data = {}
#     case_data['id'] = case.id
#     case_data['code'] = case.code
#     case_data['citizen'] = case.citizen
#
#     return jsonify({'user' : case_data})

@app.route('/register_optician', methods=["POST"])
@token_required
def register_optician():
    content = request.json
    optician = Optician(name=content["name"], surname=content["surname"], email=content["email"],
                        password=content["password"])
    db.session.add(optician)
    db.session.commit()

    return jsonify({"created_id": optician.id})