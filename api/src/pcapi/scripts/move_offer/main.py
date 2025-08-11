import argparse

from pcapi import settings
from pcapi.app import app
from pcapi.models import db
from pcapi.scripts.move_offer.move_batch_offer import _move_all_venue_offers


app.app_context().push()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="mais qui va lire ça ?")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--origin", default=None)
    parser.add_argument("--destination", default=None)
    args = parser.parse_args()

    dry_run = args.dry_run
    origin = args.origin
    destination = args.destination

    try:
        db.session.execute("SET SESSION statement_timeout = '1200s'")  # 20 minutes
        _move_all_venue_offers(dry_run=dry_run, origin=origin, destination=destination)
        db.session.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
    except:
        db.session.rollback()
        raise
    else:
        if args.dry_run:
            db.session.rollback()
        else:
            db.session.commit()
