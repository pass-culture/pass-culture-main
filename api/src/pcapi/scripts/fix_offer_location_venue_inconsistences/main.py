"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41532-reprise-des-incoherences-de-venue-entre-loffre-et-sa-localisation \
  -f NAMESPACE=fix_offer_location_venue_inconsistences \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

import pcapi.core.offerers.api as offerers_api
import pcapi.core.offers.models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def main(offer_ids: list[int]) -> None:
    for offer_id in offer_ids:
        offer = (
            db.session.query(offers_models.Offer)
            .options(
                sa_orm.joinedload(offers_models.Offer.venue),
                sa_orm.joinedload(offers_models.Offer.offererAddress),
            )
            .filter(offers_models.Offer.id == offer_id)
            .one()
        )
        assert offer.offererAddress  # sacrifice to please the gods of typing
        offer.offererAddress = offerers_api.get_or_create_offer_location(
            offerer_id=offer.venue.managingOffererId,
            venue_id=offer.venueId,
            address_id=offer.offererAddress.addressId,
            label=offer.offererAddress.label,
        )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--offer-ids", nargs="+", type=int, required=True)
    args = parser.parse_args()

    with atomic():
        main(offer_ids=args.offer_ids)
        if args.apply:
            logger.info("Finished")
        else:
            mark_transaction_as_invalid()
            logger.info("Finished dry run, rollback")
