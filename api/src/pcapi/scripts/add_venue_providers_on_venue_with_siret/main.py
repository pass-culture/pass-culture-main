"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-36399-add-venue-providers-on-venue-with-siret/api/src/pcapi/scripts/add_venue_providers_on_venue_with_siret/main.py

"""

import argparse
import csv
import logging
import os

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import VenueProvider
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "venue_id"


def _write_modifications(modifications: list[tuple[int, str]], filename: str) -> None:
    # csv output to check what has been done and what failed
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/{filename}"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([VENUE_ID_HEADER, "Modification"])
        writer.writerows(modifications)


@atomic()
def main(not_dry: bool) -> None:
    log_modifications: list[tuple[int, str]] = []
    log_fails: list[tuple[int, str]] = []
    venues_without_siret_with_providers: list[Venue] = (
        db.session.query(Venue)
        .join(Venue.venueProviders)
        .filter(
            Venue.siret.is_(None),
            sa.exists().where(VenueProvider.venueId == Venue.id).correlate(Venue),
        )
        .options(
            sa_orm.load_only(Venue.id, Venue.siret, Venue.managingOffererId),
            sa_orm.joinedload(Venue.venueProviders).load_only(
                VenueProvider.venueId,
                VenueProvider.providerId,
            ),
        )
        .all()
    )

    venues_with_siret_by_offerer_query = (
        db.session.query(sa.func.min(Venue.id))
        .filter(Venue.siret.is_not(None))
        # .options(sa_orm.load_only(Venue.managingOffererId))
        .having(sa.func.count(Venue.id) == 1)
        .group_by(Venue.managingOffererId)
    )

    for venue in venues_without_siret_with_providers:
        venue_id_with_siret = venues_with_siret_by_offerer_query.filter(
            Venue.managingOffererId == venue.managingOffererId
        ).scalar()

        new_providers: list[VenueProvider] = [
            VenueProvider(venueId=venue_id_with_siret, providerId=venue_provider.providerId)
            for venue_provider in venue.venueProviders
        ]
        print(f"Venue {venue.id} will be synch. with those providers {new_providers}")
        try:
            with atomic():
                db.session.add_all(new_providers)
                db.session.flush()
        except sa_exc.IntegrityError as error:
            log_fails.append((venue.id, f"Provider already exists on venue. \n {error}"))
            continue

        log_modifications.append((venue_id_with_siret, f"Adding providers {new_providers}"))
        for venue_provider in new_providers:
            history_api.add_action(
                history_models.ActionType.SYNC_VENUE_TO_PROVIDER,
                author=None,
                venue=venue,
                provider_name=venue_provider.provider.name,
            )
        logger.info("Adding providers %s on venue %s", new_providers, venue.id)

    _write_modifications(log_modifications, "add_providers.csv")
    _write_modifications(log_fails, "add_providers_fails.csv")

    if not not_dry:
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
