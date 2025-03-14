import argparse

from pcapi.core.bookings.api import recompute_dnBookedQuantity
from pcapi.flask_app import app
from pcapi.models import db


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="Recompute dnBookedQuantity")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    recompute_dnBookedQuantity([28707882, 25405121, 25405079, 292414619])
    if args.not_dry:
        db.session.commit()
    else:
        db.session.rollback()
