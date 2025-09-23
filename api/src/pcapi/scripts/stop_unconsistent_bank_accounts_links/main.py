"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/master/api/src/pcapi/scripts/stop_unconsistent_bank_accounts_links/main.py

Stop venue bank account links when bank account is unconsistent between information in DS and our database.
"""

import argparse
import datetime
import logging

import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)

DS_APPLICATION_IDS = [
    10982374,
    15855686,
    16581499,
    17329285,
    17707407,
    18468174,
    18940530,
    19384332,
    19463055,
    19472805,
    19493945,
    19649839,
    18849984,
    19891322,
    17983076,
    20062863,
    20196703,
    20200218,
    20240641,
    20253840,
    20265419,
    20272337,
    20287293,
    20405576,
    20843676,
    21025720,
    21051090,
    20333879,
    21264002,
    20482608,
    21313504,
    21349431,
    21380338,
    21504979,
    21509075,
    21600718,
    21703440,
    21779542,
    21856979,
    21887516,
    21987727,
    21985452,
    22128789,
    22169764,
    22318973,
    22527013,
    22587040,
    22911964,
    22919889,
    22926158,
    23025080,
    23574126,
    23593399,
    23656567,
    23711688,
    23988766,
    24016888,
    24414803,
    24435608,
    24601382,
    24755505,
    24803821,
    24831132,
    25075710,
]


def main(not_dry: bool) -> None:
    links = (
        db.session.query(offerers_models.VenueBankAccountLink)
        .join(offerers_models.VenueBankAccountLink.bankAccount)
        .filter(
            finance_models.BankAccount.dsApplicationId.in_(DS_APPLICATION_IDS),
            offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
        )
        .options(
            sa_orm.contains_eager(offerers_models.VenueBankAccountLink.bankAccount),
            sa_orm.joinedload(offerers_models.VenueBankAccountLink.venue),
        )
        .order_by(finance_models.BankAccount.dsApplicationId)
        .all()
    )
    for link in links:
        logger.info(
            "%s stop link between venue %d (SIRET %s) and bank account %d (DS: %d)",
            "" if not_dry else "would",
            link.venueId,
            link.venue.siret,
            link.bankAccountId,
            link.bankAccount.dsApplicationId,
        )
        link.timespan = db_utils.make_timerange(link.timespan.lower, datetime.datetime.utcnow())
        db.session.add(link)
        history_api.add_action(
            author=None,
            venue=link.venue,
            bank_account=link.bankAccount,
            action_type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            comment=(
                "Compte bancaire incohérent entre la base de données et Démarches-Simplifiées, "
                "lien désactivé par sécurité, acteur culturel contacté - PC-38060"
            ),
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
