"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=staging   -f BRANCH_NAME=ogeber/pc-37989-soft-delete-venues-without-offers   -f NAMESPACE=soft_delete_venues_without_offers   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
import typing

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectivePlaylist
from pcapi.core.history import models as history_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.providers.api import delete_venue_provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "Venue ID"


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _venue_can_be_deleted(venue: Venue) -> bool:
    if db.session.query(Offer).filter(Offer.venueId == venue.id).limit(1).scalar():
        logger.info("Venue %s has offer(s)", venue.id)
        return False

    if db.session.query(CollectiveOffer).filter(CollectiveOffer.venueId == venue.id).limit(1).scalar():
        logger.info("Venue %s has collective offer(s)", venue.id)
        return False

    if db.session.query(CollectiveOfferTemplate).filter(CollectiveOfferTemplate.venueId == venue.id).limit(1).scalar():
        logger.info("Venue %s has collective offer template(s)", venue.id)
        return False

    if db.session.query(CollectivePlaylist).filter(CollectivePlaylist.venueId == venue.id).limit(1).scalar():
        logger.info("Venue %s has collective playlist(s)", venue.id)
        return False

    if (
        db.session.query(Venue)
        .filter(Venue.managingOffererId == venue.managingOffererId, Venue.isSoftDeleted.is_(False))
        .count()
        == 1
    ):
        logger.info("Venue %s is single on its offerer", venue.id)
        return False

    if (
        db.session.query(Venue)
        .filter(
            Venue.id == venue.id,
            sa.or_(
                Venue.isPermanent.is_(True),
                Venue.isOpenToPublic.is_(True),
            ),
        )
        .scalar()
    ):
        logger.info("Venue %s is either permanent or open to public", venue.id)
        return False

    return True


def main() -> None:
    rows = list(_read_csv_file("venues_without_offers"))
    venue_ids = {row[VENUE_ID_HEADER] for row in rows}

    user = db.session.query(User).filter_by(id=5752883).one()
    venues_without_offers = db.session.query(Venue).filter(Venue.id.in_(venue_ids))
    venue_provider_list = db.session.query(VenueProvider).filter(VenueProvider.venueId.in_(venue_ids)).all()

    venue_providers = {vp.venueId: vp for vp in venue_provider_list}

    for venue in venues_without_offers.all():
        if not _venue_can_be_deleted(venue):
            continue

        if vp := venue_providers.get(venue.id, None):
            logger.info("Hard deleting venue provider %s", str(vp.id))
            delete_venue_provider(vp, user, send_email=False)

        venue.isSoftDeleted = True
        logger.info("Soft deleting venue %s", str(venue.id))
        db.session.add(
            history_models.ActionHistory(
                venueId=venue.id,
                authorUser=user,
                actionType=history_models.ActionType.VENUE_SOFT_DELETED,
                comment="Venue without Offer Soft Deleted (PC-37989)",
            )
        )
        db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
