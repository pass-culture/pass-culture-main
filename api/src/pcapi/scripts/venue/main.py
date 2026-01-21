"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=bdalbianco/PC-38256_set_venue_activity_for_simple_venue_type_code   -f NAMESPACE=venue   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import update

from pcapi.app import app
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    venue_types_to_set = [
        {"type_code": VenueTypeCode.ARTISTIC_COURSE, "activity": Activity.ART_SCHOOL},
        {"type_code": VenueTypeCode.BOOKSTORE, "activity": Activity.BOOKSTORE},
        {"type_code": VenueTypeCode.CONCERT_HALL, "activity": Activity.PERFORMANCE_HALL},
        {"type_code": VenueTypeCode.CREATIVE_ARTS_STORE, "activity": Activity.CREATIVE_ARTS_STORE},
        {"type_code": VenueTypeCode.DISTRIBUTION_STORE, "activity": Activity.DISTRIBUTION_STORE},
        {"type_code": VenueTypeCode.FESTIVAL, "activity": Activity.FESTIVAL},
        {"type_code": VenueTypeCode.GAMES, "activity": Activity.GAMES_CENTRE},
        {"type_code": VenueTypeCode.LIBRARY, "activity": Activity.LIBRARY},
        {"type_code": VenueTypeCode.MOVIE, "activity": Activity.CINEMA},
        {"type_code": VenueTypeCode.MUSEUM, "activity": Activity.MUSEUM},
        {"type_code": VenueTypeCode.MUSICAL_INSTRUMENT_STORE, "activity": Activity.MUSIC_INSTRUMENT_STORE},
        {"type_code": VenueTypeCode.PERFORMING_ARTS, "activity": Activity.PERFORMANCE_HALL},
        {"type_code": VenueTypeCode.RECORD_STORE, "activity": Activity.RECORD_STORE},
        {"type_code": VenueTypeCode.SCIENTIFIC_CULTURE, "activity": Activity.SCIENCE_CENTRE},
        {"type_code": VenueTypeCode.TRAVELING_CINEMA, "activity": Activity.CINEMA},
    ]
    for venue_type in venue_types_to_set:
        db.session.execute(
            update(Venue)
            .where(Venue.isOpenToPublic == True, Venue.venueTypeCode == venue_type["type_code"], Venue.activity == None)
            .values(activity=venue_type["activity"])
        )


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
