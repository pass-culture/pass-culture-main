import argparse
import logging

from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.models import db


NEW_VENUE_ID = 127134
logger = logging.getLogger(__name__)


def update_pricing_and_event_venue(not_dry: bool = False) -> None:
    finance_event_to_move = (
        finance_models.FinanceEvent.query.join(educational_models.CollectiveBooking)
        .filter(finance_models.FinanceEvent.venueId != educational_models.CollectiveBooking.venueId)
        .one()
    )
    logger.info("FinanceEvent being moved : %s", finance_event_to_move.id)

    finance_event_to_move.venueId = NEW_VENUE_ID
    db.session.add(finance_event_to_move)

    pricing_to_move = (
        finance_models.Pricing.query.join(educational_models.CollectiveBooking)
        .filter(finance_models.Pricing.venueId != educational_models.CollectiveBooking.venueId)
        .one()
    )
    logger.info("Pricing being moved : %s", pricing_to_move.id)
    pricing_to_move.venueId = NEW_VENUE_ID
    db.session.add(pricing_to_move)

    if not_dry:
        logger.info("Commit !")
        db.session.commit()
    else:
        logger.info("Rollback !")
        db.session.rollback()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Update venue for this pricing and financeEvent")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    update_pricing_and_event_venue(args.not_dry)
