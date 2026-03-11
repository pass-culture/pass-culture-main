import argparse

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
from pcapi.models import db
from pcapi.scripts.move_offer.move_batch_offer import _move_all_venue_offers


app.app_context().push()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="mais qui va lire ça ?")
    parser.add_argument("--apply", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--origin", default=None)
    parser.add_argument("--destination", default=None)
    args = parser.parse_args()

    apply = args.apply
    origin = args.origin
    destination = args.destination

    try:
        db.session.execute(sa.text("SET SESSION statement_timeout = '1200s'"))  # 20 minutes
        _move_all_venue_offers(apply=apply, origin=origin, destination=destination)
        db.session.execute(sa.text(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))
    except:
        db.session.rollback()
        raise
    else:
        if args.apply:
            db.session.commit()
        else:
            db.session.rollback()
