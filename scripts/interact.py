""" interact """
import os
from flask import Flask

from models.db import db

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', '+%+3Q23!zbc+!Dd@')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# IMPORT A LOT OF TOOLS TO MAKE THEM AVAILABLE
# IN THE PYTHON SHELL
from sqlalchemy import *
with app.app_context():
    import models.install
    from models import *
from utils.content import *
from utils.credentials import *
from utils.human_ids import *
from utils.includes import *
from utils.printer import *
from utils.token import *
