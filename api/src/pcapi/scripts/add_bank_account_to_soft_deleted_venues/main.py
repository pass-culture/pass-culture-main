"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/master/api/src/pcapi/scripts/add_bank_account_to_soft_deleted_venues/main.py

"""

import argparse
import logging
from datetime import datetime

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    venues_that_need_bank_account = (
        db.session.query(offerers_models.Venue)
        .execution_options(include_deleted=True)
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
        )
        .filter(offerers_models.Venue.isSoftDeleted == True, offerers_models.VenueBankAccountLink.venueId == None)
    )
    for venue in venues_that_need_bank_account.all():
        # Il existe 2 cas d'ActionHistory pour la régul (actionType = VENUE_REGULARIZATION)
        # - pour le transfert d'offre, ce qui nous interesse, avec un "extraData" = {"destination_venue_id": XXXX} et "comment" = None
        # - un autre pour l'ajout de pricing point sur la venue, "comment" avec une valeur
        venue_action_history = (
            db.session.query(history_models.ActionHistory)
            .filter(
                history_models.ActionHistory.venueId == venue.id,
                history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
                history_models.ActionHistory.comment == None,
            )
            .one()
        )
        destination_venue_bank_account_link = (
            db.session.query(offerers_models.VenueBankAccountLink)
            .filter(
                offerers_models.VenueBankAccountLink.venueId
                == venue_action_history.extraData.get("destination_venue_id"),
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            )
            .one_or_none()
        )
        if destination_venue_bank_account_link:
            link = offerers_models.VenueBankAccountLink(
                bankAccount=destination_venue_bank_account_link.bankAccount,
                venue=venue,
                timespan=(venue_action_history.actionDate,),
            )
            logger.info(
                "Ajout du compte bancaire %d pour la venue %d",
                destination_venue_bank_account_link.bankAccountId,
                venue.id,
            )
            action_history = history_models.ActionHistory(
                actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                venue=venue,
                bankAccount=destination_venue_bank_account_link.bankAccount,
            )
            db.session.add_all((link, action_history))


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        db.session.commit()
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")
