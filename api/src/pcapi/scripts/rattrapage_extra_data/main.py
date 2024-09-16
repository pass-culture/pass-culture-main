import argparse
import logging

from pcapi.core.offers.models import Offer
from pcapi.models import db


logger = logging.getLogger(__name__)

EXTRA_DATA_TO_CLEAR = {
    "ean",
    "isbn",
    "visa",
    "author",
    "gtl_id",
    "speaker",
    "showType",
    "musicType",
    "performer",
    "showSubType",
    "musicSubType",
    "stageDirector",
}


def fix_extra_data(do_update: bool, offer_ids: list) -> None:
    logger.info("(PC-31797) script to clear extra data started")
    offer_list = Offer.query.filter(Offer.id.in_(offer_ids)).all()
    unprocessed_offer_list = set()
    for offer in offer_list:
        if offer.extraData:
            for key, value in offer.extraData:
                if value == "" and key in EXTRA_DATA_TO_CLEAR:
                    try:
                        offer.extraData.pop(key)
                    except KeyError:
                        logger.info("Failed to remove %s from offer with ID %d", key, offer.id)
            db.session.add(offer)
        else:
            unprocessed_offer_list.add(offer.id)
    logger.info("Offer IDs that have not been processed : %s", unprocessed_offer_list)
    if do_update:
        db.session.commit()
    else:
        db.session.rollback()
    logger.info("(PC-31797) script to clear extra data finished")


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Remove empty fields from extra data for given offer ids")
    parser.add_argument("--offer-ids", nargs="+", help="Liste d'Offer IDs", required=True)
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    fix_extra_data(do_update=args.not_dry, offer_ids=args.offer_ids)
