import argparse
import logging

from pcapi.core.bookings import api as bookings_api
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="Recount dnBookedQuantity")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    stock_ids = [
        161231792,
        265485062,
        247855404,
        277199400,
        265099201,
        255351801,
        277132225,
        113378086,
        265394528,
        247855403,
    ]

    for id_ in stock_ids:
        bookings_api.recompute_dnBookedQuantity(stock_ids)

    if args.not_dry:
        db.session.commit()
    else:
        db.session.rollback()
