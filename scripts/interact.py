""" interact """
import os

from flask import Flask
from mailjet_rest import Client

from models.db import db
from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', '+%+3Q23!zbc+!Dd@')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
db.init_app(app)
db.app = app

# IMPORT A LOT OF TOOLS TO MAKE THEM AVAILABLE
# IN THE PYTHON SHELL
from domain import *
from recommendations_engine import *
from local_providers import *
from models import *
from repository.offer_queries import *
from repository.user_queries import *
from sandboxes import *
from sqlalchemy import *
from utils.config import *
from utils.credentials import *
from utils.distance import *
from utils.human_ids import *
from utils.import_module import *
from utils.includes import *
from utils.logger import *
from utils.token import *
from scripts.beneficiary import remote_import
from scripts.booking import *
