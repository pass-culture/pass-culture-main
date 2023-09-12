from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository


def find_educational_deposit_by_institution_id_and_year(
    educational_institution_id: int,
    educational_year_id: str,
) -> educational_models.EducationalDeposit | None:
    return educational_repository.find_educational_deposit_by_institution_id_and_year(
        educational_institution_id=educational_institution_id, educational_year_id=educational_year_id
    )
