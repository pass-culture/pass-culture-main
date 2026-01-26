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
import itertools
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.educational import models as educationnal_models
from pcapi.core.offerers import models as offerer_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


@atomic()
def _process_venues(venue_ids: list[int], not_dry: bool) -> None:
    for venue_id in venue_ids:
        collective_offer_domains = set(
            db.session.query(educationnal_models.EducationalDomain)
            .join(educationnal_models.EducationalDomain.collectiveOffers)
            .filter(
                educationnal_models.CollectiveOffer.venueId == venue_id,
                educationnal_models.CollectiveOffer.validation.not_in(
                    [
                        offer_mixin.OfferValidationStatus.REJECTED,
                        offer_mixin.OfferValidationStatus.PENDING,
                        offer_mixin.OfferValidationStatus.DRAFT,
                    ]
                ),
            )
            .distinct()
            .all()
        )
        collective_offer_template_domains = set(
            db.session.query(educationnal_models.EducationalDomain)
            .join(educationnal_models.EducationalDomain.collectiveOfferTemplates)
            .filter(
                educationnal_models.CollectiveOfferTemplate.venueId == venue_id,
                educationnal_models.CollectiveOfferTemplate.validation.not_in(
                    [
                        offer_mixin.OfferValidationStatus.REJECTED,
                        offer_mixin.OfferValidationStatus.PENDING,
                        offer_mixin.OfferValidationStatus.DRAFT,
                    ]
                ),
            )
            .distinct()
            .all()
        )
        domains = collective_offer_domains | collective_offer_template_domains
        if len(domains):
            logger.warning("Setting venue id %s with domains %s", venue_id, [domain.name for domain in domains])
            db.session.execute(
                sa.insert(educationnal_models.EducationalDomainVenue),
                [{"educationalDomainId": domain.id, "venueId": venue_id} for domain in domains],
            )

    if not not_dry:
        mark_transaction_as_invalid()


def main(not_dry: bool) -> None:
    venue_ids = [
        venue_id
        for (venue_id,) in db.session.query(offerer_models.Venue)
        .filter(
            offerer_models.Venue.isOpenToPublic.is_(False),
            offerer_models.Venue.collectiveDomains == None,
        )
        .with_entities(offerer_models.Venue.id)
        .all()
    ]
    logger.info("Found %s venues to process", len(venue_ids))
    for batched_venues_ids in list(itertools.batched(venue_ids, 100)):
        _process_venues(batched_venues_ids, not_dry)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
