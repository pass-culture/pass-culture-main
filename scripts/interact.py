""" interact """
from flask import Flask
import os
from sqlalchemy import func, select

from models.db import db

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET', '+%+3Q23!zbc+!Dd@')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    import models.install

"""
from models import *
from utils.content import *
from utils.credentials import *
#from utils.context import with_app_context
from utils.human_ids import *
from utils.includes import *
from utils.printer import *
from utils.token import *
"""

# necessary to have the query of model bound with the app context
#with_app_context(app)

# add some cool local variables
"""
locals().update(app.model)
session = app.db.session

client_user = User.query\
           .filter_by(email='arnaud.betremieux@beta.gouv.fr')\
           .first()
pro_user = User.query\
           .filter_by(email='erwan.ledoux@beta.gouv.fr')\
           .first()
def change_password(user, password):
    if type(user) != User:
        user = User.query.filter_by(email=user).one()
    user.setPassword(password)
    user = session.merge(user)
    PcObject.check_and_save(user)
"""

# COOL CLI
#printify(listify(app.datascience.get_occasions(client_user, 2), offers_includes, cut=10))
