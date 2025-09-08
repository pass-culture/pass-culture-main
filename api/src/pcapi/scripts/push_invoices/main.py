"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/BSR-test-cegid-in-staging/api/src/pcapi/scripts/push_invoices/main.py

"""

import logging

import pcapi.core.finance.external as finance_external
from pcapi.app import app


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.app_context().push()

    finance_external.push_invoices(0)
