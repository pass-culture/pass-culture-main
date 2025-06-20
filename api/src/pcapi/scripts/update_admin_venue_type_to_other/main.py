"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36325-api-modifier-toutes-les-venues-qui-sont-lieu-administratif-en-autre/api/src/pcapi/scripts/update_admin_venue_type_to_other/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core import search
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> list[int]:
    venue_query = db.session.query(offerers_models.Venue).filter(
        offerers_models.Venue.venueTypeCode == offerers_models.VenueTypeCode.ADMINISTRATIVE.name
    )
    venue_ids = list(venue_query.with_entities(offerers_models.Venue.id).all())
    venue_query.update({offerers_models.Venue.venueTypeCode: offerers_models.VenueTypeCode.OTHER.name})
    return venue_ids


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    venue_ids = main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
        search.async_index_venue_ids(
            venue_ids,
            reason=search.IndexationReason.VENUE_UPDATE,
        )
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
