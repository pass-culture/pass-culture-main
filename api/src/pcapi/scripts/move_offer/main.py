"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36167-api-batch-move-offer-corriger-la-lenteur-du-move-offers/api/src/pcapi/scripts/move_offer/main.py

"""

import argparse
import logging

from pcapi import settings
from pcapi.app import app
from pcapi.models import db
from pcapi.scripts.move_offer.move_batch_offer import _move_all_venue_offers


logger = logging.getLogger(__name__)


def main(not_dry: bool, origin: int | None, destination: int | None) -> None:
    db.session.execute("SET SESSION statement_timeout = '1200s'")  # 20 minutes
    _move_all_venue_offers(not_dry=not_dry, origin=origin, destination=destination)
    db.session.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")

    if not_dry:
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--origin", type=int)
    parser.add_argument("--destination", type=int)
    args = parser.parse_args()

    main(not_dry=args.not_dry, origin=args.origin, destination=args.destination)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
