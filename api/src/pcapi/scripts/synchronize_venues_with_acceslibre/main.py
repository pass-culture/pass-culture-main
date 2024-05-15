import argparse
import logging

import sqlalchemy as sa

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def synchronize_venues_with_acceslibre(venue_ids: list[int], dry_run: bool = True) -> None:
    for venue_id in venue_ids:
        venue = offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()
        if venue is None:
            logger.warning("Venue with id %s not found", venue_id)
            continue

        offerers_api.set_accessibility_provider_id(venue)
        if not venue.accessibilityProvider:
            logger.info("No match found at acceslibre for Venue %s ", venue_id)
            continue

        offerers_api.set_accessibility_infos_from_provider_id(venue)
        db.session.add(venue)

    if not dry_run:
        try:
            db.session.commit()
        except sa.exc.SQLAlchemyError:
            logger.exception("Could not update venues %s", venue_ids)
            db.session.rollback()
    else:
        db.session.rollback()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("venue_ids", type=int, nargs=-1, required=True)
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()
    with app.app_context():
        synchronize_venues_with_acceslibre(dry_run=args.dry_run, venue_ids=args.venue_ids)


if __name__ == "__main__":
    main()
