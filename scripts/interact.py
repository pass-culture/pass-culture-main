""" interact """
import os
from flask import Flask

from local_providers.install import install_local_providers
from models.db import db
from models.install import install_models

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', '+%+3Q23!zbc+!Dd@')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
db.app = app

with app.app_context():
    install_models()
    install_local_providers()

# IMPORT A LOT OF TOOLS TO MAKE THEM AVAILABLE
# IN THE PYTHON SHELL
from domain import *
from recommendations_engine import *
from local_providers import *
from models import *
from repository.offer_queries import *
from sandboxes import *
from sqlalchemy import *
from utils.content import *
from utils.config import *
from utils.credentials import *
from utils.distance import *
from utils.human_ids import *
from utils.import_module import *
from utils.includes import *
from utils.logger import *
from utils.printer import *
from utils.token import *
