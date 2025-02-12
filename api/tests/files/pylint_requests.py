"""This is a test file for our checker in `pcapi.utils.pylint`.

This file is NOT run by pytest, which is why it does not contain any
assertion.
"""

# ruff: noqa

import requests  # should yield a warning
from requests import Session  # should yield a warning
import requests.session as requests_session  # should yield a warning
from requests.session import Session  # should yield a warning

from pcapi.utils import requests
import pcapi.utils.requests
from pcapi.utils.requests import Session
