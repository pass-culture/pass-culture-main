import datetime
import decimal

from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.repository import repository


def create_educational_deposit(
    parameters: educational_models.EducationalDepositParameters,
) -> educational_models.EducationalDeposit:
    educational_deposit = educational_models.EducationalDeposit(
        educationalYearId=parameters.educational_year_id,
        educationalInstitutionId=parameters.educational_institution_id,
        amount=decimal.Decimal(parameters.deposit_amount),
        isFinal=False,
        dateCreated=datetime.datetime.utcnow(),
        ministry=parameters.ministry,
    )
    repository.save(educational_deposit)

    return educational_deposit


def find_educational_deposit_by_institution_id_and_year(
    educational_institution_id: int,
    educational_year_id: str,
) -> educational_models.EducationalDeposit | None:
    return educational_repository.find_educational_deposit_by_institution_id_and_year(
        educational_institution_id=educational_institution_id, educational_year_id=educational_year_id
    )
