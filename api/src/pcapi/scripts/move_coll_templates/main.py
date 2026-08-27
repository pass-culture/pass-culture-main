"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43417-move-collective-template \
  -f NAMESPACE=move_coll_templates \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(venue_id: int, template_ids: list[int]) -> None:
    destination_venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .options(sa_orm.joinedload(offerers_models.Venue.managingOfferer))
        .one()
    )
    templates = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .filter(educational_models.CollectiveOfferTemplate.id.in_(template_ids))
        .all()
    )
    for template in templates:
        template.venue = destination_venue
        if template.offererAddress:
            template.offererAddress = offerers_api.get_or_create_offer_location(
                offerer_id=destination_venue.managingOffererId,
                address_id=template.offererAddress.addressId,
                venue_id=venue_id,
                label=template.offererAddress.label,
            )
        db.session.add(template)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--venue-id", type=int, required=True)
    parser.add_argument("--template-ids", type=int, nargs="+", required=True)
    args = parser.parse_args()

    main(args.venue_id, args.template_ids)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
