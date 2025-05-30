"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-35685-eacback-rattrapage-offre-vitrine-collective-sans-domaine-ou-programme/api/src/pcapi/scripts/collective_offer_without_domain/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    domain = (
        db.session.query(models.EducationalDomain)
        .filter(models.EducationalDomain.name == "Univers du livre, de la lecture et des écritures")
        .one()
    )

    offers_to_update = (
        db.session.query(models.CollectiveOffer)
        .outerjoin(
            models.CollectiveOfferDomain, models.CollectiveOffer.id == models.CollectiveOfferDomain.collectiveOfferId
        )
        .filter(
            models.CollectiveOffer.nationalProgramId.is_not(None),
            models.CollectiveOfferDomain.collectiveOfferId.is_(None),
        )
        .all()
    )

    logger.info(
        "Found %s collective offers to update: %s", len(offers_to_update), [offer.id for offer in offers_to_update]
    )

    for offer in offers_to_update:
        offer.domains.append(domain)

        if offer.name != "Jeunes en librairie Auvergne-Rhône-Alpes 2023-2024":
            raise ValueError(f"Offer {offer.id} should not be updated")

    db.session.flush()


if __name__ == "__main__":
    logger.info("Starting script")
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
