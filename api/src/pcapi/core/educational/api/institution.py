from datetime import datetime
from decimal import Decimal
import typing

from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
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
    uai: str | None,
) -> educational_models.EducationalInstitution:
    return educational_repository.search_educational_institution(
        educational_institution_id=educational_institution_id,
        name=name,
        city=city,
        postal_code=postal_code,
        institution_type=institution_type,
        limit=limit,
        uai=uai,
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


def import_deposit_institution_data(
    data: dict[str, Decimal],
    educational_year: educational_models.EducationalYear,
    ministry: educational_models.Ministry,
    final: bool,
    conflict: str,
) -> None:
    adage_institutions = {
        i.uai: i for i in adage_client.get_adage_educational_institutions(ansco=educational_year.adageId)
    }
    db_institutions = {
        institution.institutionId: institution for institution in educational_models.EducationalInstitution.query.all()
    }
    for uai, amount in data.items():
        created = False
        adage_institution = adage_institutions.get(uai)
        if not adage_institution:
            print(f"\033[91mERROR: UAI:{uai} not found in adage.\033[0m")
            return

        db_institution = db_institutions.get(uai, None)
        institution_type = INSTITUTION_TYPES.get(adage_institution.sigle, adage_institution.sigle)
        if db_institution:
            db_institution.institutionType = institution_type
            db_institution.name = adage_institution.libelle
            db_institution.city = adage_institution.communeLibelle
            db_institution.postalCode = adage_institution.codePostal
            db_institution.email = adage_institution.courriel or ""
            db_institution.phoneNumber = adage_institution.telephone or ""
            db_institution.isActive = True
        else:
            created = True
            print(f"\033[33mWARNING: UAI:{uai} not found in db, creating institution.\033[0m")
            db_institution = educational_models.EducationalInstitution(
                institutionId=uai,
                institutionType=institution_type,
                name=adage_institution.libelle,
                city=adage_institution.communeLibelle,
                postalCode=adage_institution.codePostal,
                email=adage_institution.courriel or "",
                phoneNumber=adage_institution.telephone or "",
                isActive=True,
            )
            db.session.add(db_institution)

        deposit = None
        if not created:
            deposit = educational_models.EducationalDeposit.query.filter(
                educational_models.EducationalDeposit.educationalYear == educational_year,
                educational_models.EducationalDeposit.educationalInstitution == db_institution,
            ).one_or_none()

        if deposit:
            if deposit.ministry != ministry and conflict == "replace":
                print(
                    f"\033[33mWARNING: Ministry changed from '{deposit.ministry.name}' to '{ministry.name}' for deposit {deposit.id}.\033[0m"
                )
                deposit.ministry = ministry
            deposit.amount = amount
            deposit.isFinal = final
        else:
            deposit = educational_models.EducationalDeposit(
                educationalYear=educational_year,
                educationalInstitution=db_institution,
                amount=amount,
                ministry=ministry,
                isFinal=final,
            )
            db.session.add(deposit)

    db.session.commit()


def get_current_year_remaining_credit(institution: educational_models.EducationalInstitution) -> Decimal:
    educational_year = educational_repository.find_educational_year_by_date(datetime.utcnow())
    assert educational_year is not None

    deposit = educational_repository.find_educational_deposit_by_institution_id_and_year(
        institution.id, educational_year.adageId
    )
    if deposit is None:
        raise exceptions.EducationalDepositNotFound()

    spent_amount = educational_repository.get_confirmed_collective_bookings_amount(
        institution.id, educational_year.adageId
    )
    return deposit.get_amount() - spent_amount
