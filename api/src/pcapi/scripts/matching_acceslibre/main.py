import argparse
import logging
from math import ceil

import click
import sqlalchemy as sa

import pcapi.core.bookings.api as booking_api  # pylint: disable=unused-import
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


def find_new_match_at_acceslibre(dry_run: bool = False, start_from_batch: int = 1) -> None:
    venues_query = (
        offerers_models.Venue.query.outerjoin(offerers_models.Venue.accessibilityProvider)
        .filter(
            offerers_models.Venue.isPermanent.is_(True),
            offerers_models.Venue.isVirtual.is_(False),
            offerers_models.AccessibilityProvider.id.is_(None),
        )
        .options(
            sa.orm.load_only(
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.street,
                offerers_models.Venue.banId,
                offerers_models.Venue.siret,
            )
        )
    )

    venues_without_acceslibre = venues_query.all()
    num_batches = ceil(len(venues_without_acceslibre) / BATCH_SIZE)
    if start_from_batch > num_batches:
        click.echo(f"Batch start max is {num_batches}")
        return

    start_batch_index = start_from_batch - 1
    for i in range(start_batch_index, num_batches):
        batch_start = i * BATCH_SIZE
        batch_end = (i + 1) * BATCH_SIZE
        for venue in venues_without_acceslibre[batch_start:batch_end]:
            offerers_api.set_accessibility_provider_id(venue)
            if venue.accessibilityProvider:
                offerers_api.set_accessibility_infos_from_provider_id(venue)
                db.session.add(venue)

        if not dry_run:
            try:
                db.session.commit()
            except sa.exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i + 1)
                db.session.rollback()
        else:
            db.session.rollback()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--start-from-batch", type=int, default=1)
    args = parser.parse_args()
    with app.app_context():
        find_new_match_at_acceslibre(dry_run=args.dry_run, start_from_batch=args.start_from_batch)


if __name__ == "__main__":
    main()
