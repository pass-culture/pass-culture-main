"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42661-api-offres-synchronisees-avec-tite-live-stocks-epagine-place-des-libraires-com-encore-publiees \
  -f NAMESPACE=update_offers_from_deactivated_sync \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
from pcapi.models import db
from pcapi.utils import transaction_manager


logger = logging.getLogger(__name__)


def main(provider_id: int, venue_ids: list[int] | None = None) -> None:
    query = db.session.query(offers_models.Offer).filter(
        offers_models.Offer.lastProviderId == provider_id,
        offers_models.Offer.publicationDatetime != None,
    )
    if venue_ids:
        query = query.filter(
            offers_models.Offer.venueId.in_(venue_ids),
        )
    logger.info("Deactivating offers for provider %s and venues %s", provider_id, venue_ids)
    offers_api.batch_activate_offers(query, activate=False)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--venue-id",
        type=int,
        required=False,
        nargs="*",
    )
    parser.add_argument("--provider-id", type=int, required=True)
    args = parser.parse_args()

    with transaction_manager.atomic():
        main(provider_id=args.provider_id, venue_ids=args.venue_id)

        if not args.apply:
            transaction_manager.mark_transaction_as_invalid()
            logger.info("Finished dry run, rollback")
        else:
            logger.info("Finished")
