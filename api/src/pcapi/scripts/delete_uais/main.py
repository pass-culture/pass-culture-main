"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36119-clean-uais/api/src/pcapi/scripts/delete_uais/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db


logger = logging.getLogger(__name__)


def process_institutions(postal_code_prefix: str) -> None:
    institutions: list[models.EducationalInstitution] = (
        db.session.query(models.EducationalInstitution)
        .filter(models.EducationalInstitution.postalCode.like(f"{postal_code_prefix}%"))
        .all()
    )
    logger.info(
        "Found %s institutions, UAIs: %s",
        len(institutions),
        ", ".join((institution.institutionId for institution in institutions)),
    )

    institution_ids = [institution.id for institution in institutions]
    deposits: list[models.EducationalDeposit] = (
        db.session.query(models.EducationalDeposit)
        .filter(models.EducationalDeposit.educationalInstitutionId.in_(institution_ids))
        .all()
    )
    logger.info("Found %s institution deposits", len(deposits))

    collective_offers: list[models.CollectiveOffer] = (
        db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.institutionId.in_(institution_ids)).all()
    )
    logger.info(
        "Found %s collective offers linked to an institution, ids: %s",
        len(collective_offers),
        ", ".join((str(offer.id) for offer in collective_offers)),
    )

    # check other related objects
    collective_bookings: list[models.CollectiveBooking] = (
        db.session.query(models.CollectiveBooking)
        .filter(models.CollectiveBooking.educationalInstitutionId.in_(institution_ids))
        .all()
    )
    if len(collective_bookings) > 0:
        raise ValueError("Found bookings linked to an institution")

    collective_offer_requests: list[models.CollectiveOfferRequest] = (
        db.session.query(models.CollectiveOfferRequest)
        .filter(models.CollectiveOfferRequest.educationalInstitutionId.in_(institution_ids))
        .all()
    )
    if len(collective_offer_requests) > 0:
        raise ValueError("Found requests linked to an institution")

    program_associations: list[models.EducationalInstitutionProgramAssociation] = (
        db.session.query(models.EducationalInstitutionProgramAssociation)
        .filter(models.EducationalInstitutionProgramAssociation.institutionId.in_(institution_ids))
        .all()
    )
    if len(program_associations) > 0:
        raise ValueError("Found program associations linked to an institution")

    playlists: list[models.CollectivePlaylist] = (
        db.session.query(models.CollectivePlaylist)
        .filter(models.CollectivePlaylist.institutionId.in_(institution_ids))
        .all()
    )
    if len(playlists) > 0:
        raise ValueError("Found playlists linked to an institution")

    # update and delete objects
    for collective_offer in collective_offers:
        collective_offer.institution = None

    for deposit in deposits:
        db.session.delete(deposit)

    for institution in institutions:
        db.session.delete(institution)

    db.session.flush()


def main() -> None:
    logger.info("Processing institutions from Polynésie Française")
    process_institutions(postal_code_prefix="987")
    logger.info("Finished processing institutions from Polynésie Française")

    logger.info("Processing institutions from Nouvelle Calédonie")
    process_institutions(postal_code_prefix="988")
    logger.info("Finished processing institutions from Nouvelle Calédonie")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
