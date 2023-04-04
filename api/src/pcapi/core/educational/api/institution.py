import typing

from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.adage_backends.serialize import AdageEducationalInstitution
from pcapi.core.educational.constants import INSTITUTION_TYPES
from pcapi.core.educational.models import EducationalInstitution
from pcapi.models import db
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


def compare_adage_and_institution(ansco: str) -> None:
    institutions = educational_models.EducationalInstitution.query.all()
    adage_institutions = adage_client.get_adage_educational_institutions(ansco=ansco)

    synchronise_adage_and_institution(institutions=institutions, adage_institutions=adage_institutions)


def synchronise_adage_and_institution(
    institutions: list[EducationalInstitution], adage_institutions: list[AdageEducationalInstitution]
) -> None:
    adage_institution_dict = {adage_institution.uai: adage_institution for adage_institution in adage_institutions}

    for institution in institutions:
        if institution.institutionId in adage_institution_dict:
            institution.isActive = True
            adage_institution = adage_institution_dict[institution.institutionId]

            institution.name = adage_institution.libelle
            institution.city = adage_institution.communeLibelle
            institution.postalCode = adage_institution.codePostal
            institution.email = adage_institution.courriel
            institution.phoneNumber = adage_institution.telephone or ""
            institution.institutionType = INSTITUTION_TYPES.get(adage_institution.sigle, institution.institutionType)
        else:
            institution.isActive = False
        repository.save(institution)
    db.session.commit()


def refund_institution(collective_booking_id: int, amount: float, ticket: str) -> None:
    """Logic for command refund_institution do not use in code it doesn't raise any exceptions."""
    booking = educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.id == collective_booking_id
    ).one_or_none()
    if not booking:
        print("Collective_booking not found.")
        return
    if booking.status != educational_models.CollectiveBookingStatus.REIMBURSED:
        print("Collective_booking is not reimbursed yet please modify it instead of refunding it.")
        return
    if amount > booking.collectiveStock.price:
        print("Refund cannot be greater than the booking price.")
        return
    deposit = educational_models.EducationalDeposit.query.filter(
        educational_models.EducationalDeposit.educationalYearId == booking.educationalYearId,
        educational_models.EducationalDeposit.educationalInstitutionId == booking.educationalInstitutionId,
    ).one_or_none()
    if not deposit:
        print("No deposit found for this booking.")
        return

    refund = educational_models.CollectiveRefund(
        amount=amount,
        ticket=ticket,
        ministry=deposit.ministry,
        educationalYearId=booking.educationalYearId,
        educationalInstitutionId=booking.educationalInstitutionId,
    )
    db.session.add(refund)
    db.session.commit()
