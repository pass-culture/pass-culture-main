"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36325-api-modifier-toutes-les-venues-qui-sont-lieu-administratif-en-autre/api/src/pcapi/scripts/update_admin_venue_type_to_other/main.py

"""

import argparse
import logging

import pcapi.core.history.models as history_models
from pcapi.app import app
from pcapi.core import search
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def add_action_history(venue_ids: list[int]) -> None:
    db.session.bulk_insert_mappings(
        history_models.ActionHistory,
        [
            {
                "actionType": history_models.ActionType.INFO_MODIFIED,
                "venueId": venue_id,
                "comment": "PC-36325",
                "extraData": {
                    "modified_info": {
                        "venueTypeCode": {
                            "old_info": offerers_models.VenueTypeCode.ADMINISTRATIVE.name,
                            "new_info": offerers_models.VenueTypeCode.OTHER.name,
                        },
                    }
                },
            }
            for venue_id in venue_ids
        ],
    )


def main(not_dry: bool) -> dict[int, str]:
    venue_query = db.session.query(offerers_models.Venue).filter(
        offerers_models.Venue.venueTypeCode == offerers_models.VenueTypeCode.ADMINISTRATIVE.name
    )
    venue_ids_to_email = dict(
        venue_query.with_entities(offerers_models.Venue.id, offerers_models.Venue.bookingEmail).all()
    )
    venue_query.update({offerers_models.Venue.venueTypeCode: offerers_models.VenueTypeCode.OTHER.name})
    add_action_history(venue_ids=list(venue_ids_to_email.keys()))
    return venue_ids_to_email


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    venue_ids_to_email = main(not_dry=args.not_dry)

    if args.not_dry:
        db.session.commit()
        for venue_id, venue_bookingEmail in venue_ids_to_email.items():
            external_attributes_api.update_external_pro(venue_bookingEmail)
        search.async_index_venue_ids(
            list(venue_ids_to_email.keys()),
            reason=search.IndexationReason.VENUE_UPDATE,
        )
        logger.info("Finished")
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
