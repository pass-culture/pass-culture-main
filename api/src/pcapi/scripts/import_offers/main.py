import argparse
import csv
import decimal
import logging
import os

from sqlalchemy import exc as orm_exc

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import national_program as national_program_api
from pcapi.models import db
from pcapi.models import offer_mixin


logger = logging.getLogger(__name__)


UAI_CODE_FIELD = "Code UAI"
NUMBER_OF_TICKETS_FIELD = "Effectif prévisionnel"
TEACHER_MAIL_FIELD = "Mail coordonnateur"
POSTAL_CODE_FIELD = "Code postal"
STUDENTS_FIELD = "Niveau de la classe"


app.app_context().push()


def import_offers(filename: str, collective_offer_template_id: int, commit: bool = False) -> None:
    template: educational_models.CollectiveOfferTemplate = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.id == collective_offer_template_id
    ).one()

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")

        for index, csv_row in enumerate(csv_rows):
            _process_csv_row(csv_row=csv_row, row_number=index + 1, template=template)

    if commit:
        logger.info("Commiting imported offers")
        db.session.commit()
    else:
        logger.info("Finished dry run for import offers")


def _process_csv_row(
    csv_row: dict[str, str], row_number: int, template: educational_models.CollectiveOfferTemplate
) -> None:
    uai = csv_row[UAI_CODE_FIELD]
    number_of_tickets = int(csv_row[NUMBER_OF_TICKETS_FIELD])
    teacher_email = csv_row[TEACHER_MAIL_FIELD]
    postal_code = csv_row[POSTAL_CODE_FIELD]
    students = csv_row[STUDENTS_FIELD]

    try:
        institution = educational_models.EducationalInstitution.query.filter(
            educational_models.EducationalInstitution.institutionId == uai
        ).one()
    except orm_exc.NoResultFound:
        logger.info("No institution found with this UAI for row %s", row_number)
        raise

    try:
        teacher = educational_models.EducationalRedactor.query.filter(
            educational_models.EducationalRedactor.email == teacher_email
        ).one()
    except orm_exc.NoResultFound:
        logger.info("No teacher found with this email for row %s, setting None", row_number)
        teacher = None

    # logic from pcapi/core/educational/api/offer.create_collective_offer minus the validation
    collective_offer = educational_models.CollectiveOffer(
        isActive=True,
        venueId=template.venueId,
        name=template.name,
        offerId=None,
        description=template.description,
        domains=template.domains,
        durationMinutes=template.durationMinutes,
        subcategoryId=template.subcategoryId,
        students=_get_students(students),
        contactEmail=template.contactEmail,
        contactPhone=template.contactPhone,
        offerVenue=template.offerVenue,
        validation=offer_mixin.OfferValidationStatus.APPROVED,
        audioDisabilityCompliant=template.audioDisabilityCompliant,
        mentalDisabilityCompliant=template.mentalDisabilityCompliant,
        motorDisabilityCompliant=template.motorDisabilityCompliant,
        visualDisabilityCompliant=template.visualDisabilityCompliant,
        interventionArea=[postal_code[:2]],  # extract department from postal code
        templateId=template.id,
        formats=template.formats,
        author=template.author,
        bookingEmails=template.bookingEmails,
        institution=institution,
        teacher=teacher,
        nationalProgramId=template.nationalProgramId,
    )
    db.session.add(collective_offer)

    if template.nationalProgramId:
        national_program_api.link_or_unlink_offer_to_program(template.nationalProgramId, collective_offer, commit=False)

    # logic from pcapi/core/educational/api/stock.create_collective_stock, minus the validation
    start = template.start
    assert start is not None
    assert template.end is not None

    collective_stock = educational_models.CollectiveStock(
        collectiveOffer=collective_offer,
        beginningDatetime=start,
        startDatetime=start,
        endDatetime=template.end,
        bookingLimitDatetime=start,
        price=decimal.Decimal(650),
        numberOfTickets=number_of_tickets,
        priceDetail=template.priceDetail,
    )
    db.session.add(collective_stock)

    try:
        db.session.flush()
    except orm_exc.SQLAlchemyError:
        logger.info("Error while flushing offer and stock for row %s", row_number)
        raise


def _get_students(column_value: str) -> list[educational_models.StudentLevels]:
    # those two values can correspond to any student level
    if "UPE2A" in column_value or "ULIS" in column_value:
        return [
            educational_models.StudentLevels.COLLEGE6,
            educational_models.StudentLevels.COLLEGE5,
            educational_models.StudentLevels.COLLEGE4,
            educational_models.StudentLevels.COLLEGE3,
            educational_models.StudentLevels.CAP1,
            educational_models.StudentLevels.CAP2,
            educational_models.StudentLevels.GENERAL2,
            educational_models.StudentLevels.GENERAL1,
            educational_models.StudentLevels.GENERAL0,
        ]

    # column value examples: "2nde professionnelle + CAP" / "CAPA 2 AAGA"
    students = set()

    if "4ème" in column_value:
        students.add(educational_models.StudentLevels.COLLEGE4)
    if "3ème" in column_value:
        students.add(educational_models.StudentLevels.COLLEGE3)

    if "CAPA 1" in column_value:
        students.add(educational_models.StudentLevels.CAP1)
    if "CAPA 2" in column_value:
        students.add(educational_models.StudentLevels.CAP2)
    if "CAP 1" in column_value:
        students.add(educational_models.StudentLevels.CAP1)
    if "CAP 2" in column_value:
        students.add(educational_models.StudentLevels.CAP2)

    if "CAP" in column_value and (
        "CAP 1" not in column_value
        and "CAP 2" not in column_value
        and "CAPA 1" not in column_value
        and "CAPA 2" not in column_value
    ):
        students.add(educational_models.StudentLevels.CAP1)
        students.add(educational_models.StudentLevels.CAP2)

    if "2nde" in column_value:
        students.add(educational_models.StudentLevels.GENERAL2)
    if "1ère" in column_value:
        students.add(educational_models.StudentLevels.GENERAL1)
    if "T " in column_value:
        students.add(educational_models.StudentLevels.GENERAL0)

    return list(students)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", required=True)
    parser.add_argument("--template-id", type=int, required=True)
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    try:
        import_offers(filename=args.filename, collective_offer_template_id=args.template_id, commit=args.not_dry)
    except:
        logger.exception("Error while importing offers")
        db.session.rollback()
        raise

    if not args.not_dry:
        logger.info("Finished dry run for import_offers, rollbacking")
        db.session.rollback()
