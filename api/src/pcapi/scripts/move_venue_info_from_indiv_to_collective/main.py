import argparse
import logging

import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
from pcapi.core.offerers.api import get_venue_by_id
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    from pcapi.flask_app import app

    with app.app_context():

        parser = argparse.ArgumentParser()
        parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
        parser.add_argument("--venue-ids", nargs="+", help="List of venues IDs to update")

        args = parser.parse_args()

        venue_ids = args.venue_ids
        modified_infos = dict()

        for venue_id in venue_ids:
            venue = get_venue_by_id(venue_id)
            if venue.description:
                venue.collectiveDescription = venue.description
                venue.description = None
                modified_infos["collectiveDescription"] = {
                    "old_info": None,
                    "new_info": venue.collectiveDescription,
                }
                modified_infos["description"] = {
                    "old_info": venue.description,
                    "new_info": None,
                }
            if venue.contact.phone_number:
                venue.collectivePhone = "+33825121202"
                venue.contact.phone_number = None
                modified_infos["contact.phone_number"] = {
                    "old_info": venue.contact.phone_number,
                    "new_info": None,
                }
                modified_infos["collectivePhone"] = {
                    "old_info": None,
                    "new_info": "+33825121202",
                }
            if venue.contact.email:
                venue.collectiveEmail = venue.contact.email
                venue.contact.email = None
                modified_infos["collectiveEmail"] = {
                    "old_info": None,
                    "new_info": venue.collectiveEmail,
                }
                modified_infos["contact.email"] = {
                    "old_info": venue.contact.email,
                    "new_info": None,
                }
            if venue.contact.website:
                venue.collectiveWebsite = venue.contact.website
                venue.contact.website = None
                modified_infos["collectiveWebsite"] = {
                    "old_info": None,
                    "new_info": venue.collectiveWebsite,
                }
                modified_infos["contact.website"] = {
                    "old_info": venue.contact.website,
                    "new_info": None,
                }
            db.session.add(venue)

        if args.dry_run:
            db.session.rollback()
            logger.info("PC-30035 : Dry run completed")
        else:
            history_api.add_action(
                history_models.ActionType.INFO_MODIFIED,
                author=None,
                venue=venue,
                comment="Informations modifiées par script",
                modified_info=modified_infos,
            )
            db.session.commit()
            logger.info(
                "PC-30035 : Informations have been transfered from individual to collective for venues %s", venue_ids
            )


if __name__ == "__main__":
    main()
