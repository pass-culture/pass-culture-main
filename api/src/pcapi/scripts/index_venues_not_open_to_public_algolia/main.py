"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=index_venues_not_open_to_public_algolia \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import itertools
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.models import Venue
from pcapi.core.search import reindex_venue_ids
from pcapi.core.search.serialization import AlgoliaSerializationMixin
from pcapi.core.search.serialization import position
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    # monkeypatch is_eligible_for_search
    def get_is_eligible_for_search(self) -> bool:  # type: ignore[no-untyped-def]
        return self.managingOfferer.isActive and self.managingOfferer.isValidated and self.hasOffers

    def serialize_venue(_cls, venue: offerers_models.Venue) -> dict:  # type: ignore[no-untyped-def]
        social_medias = getattr(venue.contact, "social_medias", {})
        has_at_least_one_bookable_offer = offerers_api.has_venue_at_least_one_bookable_offer(venue)

        obj_to_index = {
            "_geoloc": position(venue),
            "activity": venue.activity,
            "adress": venue.offererAddress.address.street,
            "audio_disability": venue.audioDisabilityCompliant,
            "banner_url": venue.bannerUrl,
            "city": venue.offererAddress.address.city,
            "date_created": venue.dateCreated.timestamp(),
            "description": venue.description,
            "email": getattr(venue.contact, "email", None),
            "facebook": social_medias.get("facebook"),
            "has_at_least_one_bookable_offer": has_at_least_one_bookable_offer,
            "instagram": social_medias.get("instagram"),
            "mental_disability": venue.mentalDisabilityCompliant,
            "motor_disability": venue.motorDisabilityCompliant,
            "name": venue.common_name,
            "objectID": venue.id,
            "offerer_name": venue.managingOfferer.name,
            "phone_number": getattr(venue.contact, "phone_number", None),
            "postalCode": venue.offererAddress.address.postalCode,
            "snapchat": social_medias.get("snapchat"),
            "tags": [criterion.name for criterion in venue.criteria],
            "twitter": social_medias.get("twitter"),
            "venue_type": venue.venueTypeCode.name,
            "visual_disability": venue.visualDisabilityCompliant,
            "website": getattr(venue.contact, "website", None),
            "open_to_public": venue.isOpenToPublic,
        }

        return obj_to_index

    setattr(Venue, "is_eligible_for_search", property(get_is_eligible_for_search))
    setattr(AlgoliaSerializationMixin, "serialize_venue", classmethod(serialize_venue))

    # get venue ids
    venue_ids = db.session.execute(sa.select(Venue.id).distinct()).scalars().all()

    # index venues
    if not_dry:
        for venues_ids_batch in itertools.batched(venue_ids, 1000):
            reindex_venue_ids(venues_ids_batch)


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
