""" interact """
import sys

from flask import Flask

from pcapi import settings
from pcapi.models.db import db


app = Flask(__name__)
app.secret_key = settings.FLASK_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
db.app = app

# pylint: disable=unused-import, wildcard-import, unused-wildcard-import
# Import various functions so that they are directly available in the Python shell.
from sqlalchemy import *

from pcapi.core.logging import install_logging
from pcapi.domain import *
from pcapi.local_providers import *
from pcapi.models import *
from pcapi.repository.offer_queries import *
from pcapi.repository.user_queries import *
from pcapi.sandboxes import *
from pcapi.scripts.beneficiary import remote_import
from pcapi.scripts.booking import *
from pcapi.settings import *
from pcapi.utils.human_ids import *
from pcapi.utils.includes import *
from pcapi.utils.token import *


# pylint: enable=unused-import, wildcard-import, unused-wildcard-import


install_logging()


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
        color = _non_printable(color)
        reset = _non_printable("\x1b[0m")

        sys.ps1 = f"{color}{env} >>> {reset}"


def _non_printable(seq):
    return f"\001{seq}\002"


set_python_prompt()
