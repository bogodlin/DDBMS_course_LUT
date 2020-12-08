# import click
# from flask.cli import with_appcontext
#
# from query_processor import db
# from .models import *
#
# @click.command(name='create_tables')
# @with_appcontext
# def create_tables():
#     db.create_all()
from query_processor import db
from query_processor.models import *
case = Case.query.all()

print(case)