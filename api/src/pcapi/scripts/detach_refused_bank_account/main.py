"""
Detach refused bank account for an offerer
"""

import argparse

from pcapi.core.finance.api import update_bank_account_venues_links
from pcapi.core.finance.models import BankAccount
from pcapi.core.users.models import User
from pcapi.models import db


BANK_ACCOUNT_ID = 35549


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Detach bank account from a venue")
    parser.add_argument("--author-id", type=int, required=True, help="author user id (in action history)")
    args = parser.parse_args()

    user = db.session.query(User).filter_by(id=args.author_id).one()
    bank_account = db.session.query(BankAccount).filter_by(id=BANK_ACCOUNT_ID).one()
    update_bank_account_venues_links(user, bank_account, set())
    db.session.commit()
