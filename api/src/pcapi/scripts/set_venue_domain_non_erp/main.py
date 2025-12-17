"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=bdalbianco/PC-39038_set_domain_for_non_ERP_venues_with_offers \
  -f NAMESPACE=set_venue_domain_non_erp \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import itertools

import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educationnal_models
from pcapi.core.offerers import models as offerer_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


@atomic()
def _process_venues(venues: list[offerer_models.Venue], not_dry: bool) -> None:
    for venue in venues:
        domains = (
            db.session.query(educationnal_models.EducationalDomain)
            .options(
                sa_orm.joinedload(educationnal_models.EducationalDomain.collectiveOffers).load_only(
                    educationnal_models.CollectiveOffer.venueId, educationnal_models.CollectiveOffer.validation
                )
            )
            .options(
                sa_orm.joinedload(educationnal_models.EducationalDomain.collectiveOfferTemplates).load_only(
                    educationnal_models.CollectiveOfferTemplate.venueId,
                    educationnal_models.CollectiveOfferTemplate.validation,
                )
            )
            .where(
                (
                    educationnal_models.EducationalDomain.collectiveOffers.any(
                        educationnal_models.CollectiveOffer.venueId == venue.id
                    ).where(
                        (educationnal_models.CollectiveOffer.validation != offer_mixin.OfferValidationStatus.REJECTED)
                        & (educationnal_models.CollectiveOffer.validation != offer_mixin.OfferValidationStatus.PENDING)
                        & (educationnal_models.CollectiveOffer.validation != offer_mixin.OfferValidationStatus.DRAFT)
                    )
                )
                | (
                    educationnal_models.EducationalDomain.collectiveOfferTemplates.any(
                        educationnal_models.CollectiveOfferTemplate.venueId == venue.id
                    ).where(
                        (
                            educationnal_models.CollectiveOfferTemplate.validation
                            != offer_mixin.OfferValidationStatus.REJECTED
                        )
                        & (
                            educationnal_models.CollectiveOfferTemplate.validation
                            != offer_mixin.OfferValidationStatus.PENDING
                        )
                        & (
                            educationnal_models.CollectiveOfferTemplate.validation
                            != offer_mixin.OfferValidationStatus.DRAFT
                        )
                    )
                )
            )
        )
        if domains.count():
            logger.warning("Setting venue id %s with domains %s", venue.id, [domain.name for domain in domains])
            venue.collectiveDomains = domains.all()

    if not not_dry:
        mark_transaction_as_invalid()


def main(not_dry: bool) -> None:
    venues = (
        db.session.query(offerer_models.Venue)
        .filter(
            offerer_models.Venue.isOpenToPublic.is_(False),
            offerer_models.Venue.collectiveDomains == None,
        )
        .options(sa_orm.load_only(offerer_models.Venue.id))
    ).all()
    logger.info("Found %s venues to process", len(venues))
    for batch in list(itertools.batched(venues, 100)):
        _process_venues(batch, not_dry)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
