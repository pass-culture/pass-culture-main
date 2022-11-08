import typing

from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.repository import repository
import pcapi.utils.postal_code as postal_code_utils


def create_educational_institution(
    institution_id: str,
    institution_data: dict[str, typing.Any],
) -> educational_models.EducationalInstitution:
    educational_institution = educational_models.EducationalInstitution(
        institutionId=institution_id, **institution_data
    )
    repository.save(educational_institution)

    return educational_institution


def get_all_educational_institutions(page: int, per_page_limit: int) -> tuple[tuple, int]:
    offset = (per_page_limit * (page - 1)) if page > 0 else 0
    return educational_repository.get_all_educational_institutions(offset=offset, limit=per_page_limit)


def get_educational_institution_department_code(
    institution: educational_models.EducationalInstitution,
) -> str:
    department_code = postal_code_utils.PostalCode(institution.postalCode).get_departement_code()
    return department_code


def search_educational_institution(
    educational_institution_id: int | None,
    name: str | None,
    institution_type: str | None,
    city: str | None,
    postal_code: str | None,
    limit: int,
) -> educational_models.EducationalInstitution:
    return educational_repository.search_educational_institution(
        educational_institution_id=educational_institution_id,
        name=name,
        city=city,
        postal_code=postal_code,
        institution_type=institution_type,
        limit=limit,
    )


def update_educational_institution_data(
    institution_id: str, institution_data: dict[str, typing.Any]
) -> educational_models.EducationalInstitution:
    educational_institution = educational_models.EducationalInstitution.query.filter_by(
        institutionId=institution_id
    ).one()
    for key, value in institution_data.items():
        setattr(educational_institution, key, value)
    return educational_institution
