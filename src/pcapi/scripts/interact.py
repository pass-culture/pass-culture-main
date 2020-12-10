""" interact """
# Loading variables should always be the first thing, before any other load
from pcapi.load_environment_variables import load_environment_variables


load_environment_variables()

import os
import sys

from flask import Flask
from mailjet_rest import Client

from pcapi import settings
from pcapi.models.db import db
from pcapi.utils.mailing import MAILJET_API_KEY
from pcapi.utils.mailing import MAILJET_API_SECRET


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "+%+3Q23!zbc+!Dd@")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version="v3")
db.init_app(app)
db.app = app

# pylint: disable=unused-import, wildcard-import, unused-wildcard-import
# Import various functions so that they are directly available in the Python shell.
from sqlalchemy import *

from pcapi.domain import *
from pcapi.local_providers import *
from pcapi.models import *
from pcapi.recommendations_engine import *
from pcapi.repository.offer_queries import *
from pcapi.repository.user_queries import *
from pcapi.sandboxes import *
from pcapi.scripts.beneficiary import old_remote_import
from pcapi.scripts.beneficiary import remote_import
from pcapi.scripts.booking import *
from pcapi.settings import *
from pcapi.utils.human_ids import *
from pcapi.utils.import_module import *
from pcapi.utils.includes import *
from pcapi.utils.logger import *
from pcapi.utils.token import *


# pylint: enable=unused-import, wildcard-import, unused-wildcard-import


def set_python_prompt():
    env = settings.ENV
    if env == "production":
        color = "\x1b[1;49;31m"  # red
    elif env == "staging":
        color = "\x1b[1;49;35m"  # purple
    elif env == "testing":
        color = "\x1b[1;49;36m"  # cyan
    else:
        color = None
    if color:
        sys.ps1 = f"{color}{env} >>>\x1b[0m "


set_python_prompt()
