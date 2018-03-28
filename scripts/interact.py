from flask import Flask
from sqlalchemy import func, select

from utils.content import *
from utils.context import with_app_context
from utils.human_ids import *
from utils.includes import *
from utils.printer import *
from utils.token import *

app = Flask(__name__)

# necessary to have the query of model bound with the app context
with_app_context(app)

# add some cool local variables
locals().update(app.model)
session = app.db.session
client_user = User.query\
           .filter_by(email='arnaud.betremieux@beta.gouv.fr')\
           .first()
pro_user = User.query\
           .filter_by(email='erwan.ledoux@beta.gouv.fr')\
           .first()
