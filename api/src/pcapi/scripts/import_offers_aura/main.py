"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-38306-import-offers-aura \
  -f NAMESPACE=import_offers_aura \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import decimal
import logging
import os

from sqlalchemy import exc as sa_exc

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db
from pcapi.models import offer_mixin


logger = logging.getLogger(__name__)

UAI_CODE_FIELD = "Code UAI"
OFFER_NAME_FIELD = "Titre de l'offre"
NUMBER_OF_TICKETS_FIELD = "Effectif prévisionnel"
STUDENTS_FIELD = "Niveau de la classe"
PRICE_FIELD = "Prix global"
PRICE_DETAIL_FIELD = "Détails sur le prix"
BOOKING_LIMIT_FIELD = "Date limite de résa"

COLLECTIVE_OFFER_TEMPLATE_ID = 99320
FILENAME = "offers_data.csv"


def main() -> None:
    template = (
        db.session.query(models.CollectiveOfferTemplate)
        .filter(models.CollectiveOfferTemplate.id == COLLECTIVE_OFFER_TEMPLATE_ID)
        .one()
    )

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{FILENAME}", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")

        for index, csv_row in enumerate(csv_rows):
            _process_csv_row(csv_row=csv_row, row_number=index + 1, template=template)


def _process_csv_row(csv_row: dict[str, str], row_number: int, template: models.CollectiveOfferTemplate) -> None:
    uai = csv_row[UAI_CODE_FIELD]
    offer_name = csv_row[OFFER_NAME_FIELD]
    number_of_tickets = int(csv_row[NUMBER_OF_TICKETS_FIELD])
    students = csv_row[STUDENTS_FIELD]
    price = decimal.Decimal(csv_row[PRICE_FIELD])
    price_detail = csv_row[PRICE_DETAIL_FIELD]

    try:
        institution = (
            db.session.query(models.EducationalInstitution)
            .filter(models.EducationalInstitution.institutionId == uai)
            .one()
        )
    except sa_exc.NoResultFound:
        logger.info("No institution found with this UAI for row %s", row_number)
        raise

    # logic from pcapi/core/educational/api/offer.create_collective_offer minus the validation
    collective_offer = models.CollectiveOffer(
        isActive=True,
        venueId=template.venueId,
        name=offer_name,
        description=template.description,
        domains=template.domains,
        durationMinutes=template.durationMinutes,
        students=_get_students(students),
        contactEmail=template.contactEmail,
        contactPhone=template.contactPhone,
        validation=offer_mixin.OfferValidationStatus.APPROVED,
        audioDisabilityCompliant=template.audioDisabilityCompliant,
        mentalDisabilityCompliant=template.mentalDisabilityCompliant,
        motorDisabilityCompliant=template.motorDisabilityCompliant,
        visualDisabilityCompliant=template.visualDisabilityCompliant,
        interventionArea=template.interventionArea,
        templateId=template.id,
        formats=template.formats,
        author=template.author,
        bookingEmails=template.bookingEmails,
        institution=institution,
        teacher=None,
        nationalProgramId=template.nationalProgramId,
        locationType=template.locationType,
        locationComment=template.locationComment,
        offererAddress=template.offererAddress,
    )
    db.session.add(collective_offer)

    # logic from pcapi/core/educational/api/stock.create_collective_stock, minus the validation
    assert template.start is not None
    assert template.end is not None

    collective_stock = models.CollectiveStock(
        collectiveOffer=collective_offer,
        startDatetime=template.start,
        endDatetime=template.end,
        bookingLimitDatetime=template.start,
        price=price,
        numberOfTickets=number_of_tickets,
        priceDetail=price_detail,
    )
    db.session.add(collective_stock)


def _get_students(column_value: str) -> list[models.StudentLevels]:
    # those two values can correspond to any student level
    if "UPE2A" in column_value or "ULIS" in column_value:
        return [
            models.StudentLevels.COLLEGE6,
            models.StudentLevels.COLLEGE5,
            models.StudentLevels.COLLEGE4,
            models.StudentLevels.COLLEGE3,
            models.StudentLevels.CAP1,
            models.StudentLevels.CAP2,
            models.StudentLevels.GENERAL2,
            models.StudentLevels.GENERAL1,
            models.StudentLevels.GENERAL0,
        ]

    # column value examples: "2nde professionnelle + CAP" / "CAPA 2 AAGA"
    students = set()

    if "4ème" in column_value:
        students.add(models.StudentLevels.COLLEGE4)
    if "3ème" in column_value:
        students.add(models.StudentLevels.COLLEGE3)

    if "CAPA 1" in column_value:
        students.add(models.StudentLevels.CAP1)
    if "CAPA 2" in column_value:
        students.add(models.StudentLevels.CAP2)
    if "CAP 1" in column_value:
        students.add(models.StudentLevels.CAP1)
    if "CAP 2" in column_value:
        students.add(models.StudentLevels.CAP2)

    if "CAP" in column_value and (
        "CAP 1" not in column_value
        and "CAP 2" not in column_value
        and "CAPA 1" not in column_value
        and "CAPA 2" not in column_value
    ):
        students.add(models.StudentLevels.CAP1)
        students.add(models.StudentLevels.CAP2)

    if "2nde" in column_value:
        students.add(models.StudentLevels.GENERAL2)
    if "1ère" in column_value:
        students.add(models.StudentLevels.GENERAL1)
    if "T " in column_value:
        students.add(models.StudentLevels.GENERAL0)

    return list(students)


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
