"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-38021-script-move-ba/api/src/pcapi/scripts/move_specific_bank_account/main.py

"""

import argparse
import logging
from datetime import datetime

import pcapi.utils.db as db_utils
from pcapi.app import app
from pcapi.core.history import api as history_api
from pcapi.core.history.models import ActionType
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


@atomic()
def main(not_dry: bool, venue_id: int, bank_account_id: int) -> None:
    if not not_dry:  # 🤪
        mark_transaction_as_invalid()

    link: VenueBankAccountLink = db.session.query(VenueBankAccountLink).filter_by(venueId=venue_id).one()
    link.timespan = db_utils.make_timerange(link.timespan.lower, datetime.utcnow())
    history_api.add_action(
        author=None,
        venue=link.venue,
        bank_account=link.bankAccount,
        action_type=ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
        comment="PC-38021 - Compte bancaire archivé",
    )
    db.session.flush()
    new_link = VenueBankAccountLink(venueId=venue_id, bankAccountId=bank_account_id, timespan=(datetime.utcnow(),))
    db.session.add(new_link)
    db.session.flush()
    history_api.add_action(
        author=None,
        venue=new_link.venue,
        bank_account=new_link.bankAccount,
        action_type=ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
        comment="PC-38021 - Ajout du compte bancaire en vue de la régularisation de cette venue",
    )
    db.session.add_all([link, new_link])


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--venue-id", type=int, required=True)
    parser.add_argument("--bank-account-id", type=int, required=True)
    args = parser.parse_args()

    main(not_dry=args.not_dry, venue_id=args.venue_id, bank_account_id=args.bank_account_id)

    if args.not_dry:
        logger.info("Finished")
