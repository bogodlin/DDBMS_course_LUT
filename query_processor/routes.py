from query_processor import app, db
from flask import flash, redirect, url_for, session, request, jsonify
import jwt
from functools import wraps
from query_processor.models import *

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#
#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']
#
#         if not token:
#             return jsonify({'message' : 'Token is missing!'}), 401
#
#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'])
#             current_user = User.query.filter_by(public_id=data['public_id']).first()
#         except:
#             return jsonify({'message' : 'Token is invalid!'}), 401
#
#         return f(current_user, *args, **kwargs)
#
#     return decorated

@app.route('/user', methods=['GET'])
@token_required
def get_all_cases(current_user):

    cases = Case.query.all()

    output = []

    for case in cases:
        case_data = {}
        case_data['public_id'] = case.public_id
        case_data['name'] = case.name
        case_data['password'] = case.password
        case_data['admin'] = case.admin
        output.append(case_data)

    return jsonify({'cases' : output})

