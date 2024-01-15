from datetime import datetime
from decimal import Decimal

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa

from pcapi.connectors.big_query.queries import InstitutionRuralLevelQuery
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.adage_backends import get_adage_educational_institutions
from pcapi.core.educational.adage_backends.serialize import AdageEducationalInstitution
from pcapi.core.educational.constants import INSTITUTION_TYPES
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.repository import find_educational_year_by_date
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db
from pcapi.repository import repository
import pcapi.utils.postal_code as postal_code_utils


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
    """Return the institution's remaining credit for the current year.
    The computation stays the same whether the deposit is final or not:

      current year deposit amount - sum of confirmed bookings amounts
    """
    educational_year = educational_repository.find_educational_year_by_date(datetime.utcnow())
    assert educational_year is not None

    deposit = educational_repository.find_educational_deposit_by_institution_id_and_year(
        institution.id, educational_year.adageId
    )
    if deposit is None:
        return Decimal(0)

    spent_amount = educational_repository.get_confirmed_collective_bookings_amount(
        institution.id, educational_year.adageId
    )

    return deposit.amount - spent_amount


def create_missing_educational_institution_from_adage(destination_uai: str) -> EducationalInstitution:
    """
    Fetch known adage institutions of the current year and create the
    missing institution inside or database if the target uai exists.
    """
    year = find_educational_year_by_date(datetime.utcnow())
    if year is None:
        raise educational_exceptions.EducationalYearNotFound()

    adage_institutions = get_adage_educational_institutions(year.adageId)
    if not adage_institutions:
        raise educational_exceptions.NoAdageInstitution()

    try:
        adage_institution = next(
            adage_institution for adage_institution in adage_institutions if adage_institution.uai == destination_uai
        )
    except StopIteration:
        raise educational_exceptions.MissingAdageInstitution()
    return create_educational_institution_from_adage(adage_institution)


def create_educational_institution_from_adage(institution: AdageEducationalInstitution) -> EducationalInstitution:
    educational_institution = EducationalInstitution(
        institutionId=institution.uai,
        institutionType=institution.sigle,
        name=institution.libelle,
        city=institution.communeLibelle,
        postalCode=institution.codePostal,
        email=institution.courriel or "",
        phoneNumber=institution.telephone or "",
        isActive=True,
    )

    repository.save(educational_institution)
    return educational_institution


def synchronise_rurality_level() -> None:
    rows = list(InstitutionRuralLevelQuery().execute())
    actual_rows = (
        e._asdict()
        for e in educational_models.EducationalInstitution.query.with_entities(
            educational_models.EducationalInstitution.id, educational_models.EducationalInstitution.ruralLevel
        )
    )

    ids_by_rurality_target: dict[int, set[educational_models.InstitutionRuralLevel]] = {}
    for row in rows:
        ids_by_rurality_target.setdefault(row.institution_rural_level, set()).add(row.institution_id)

    ids_by_rurality_actual: dict[int, set[educational_models.InstitutionRuralLevel]] = {}
    for row in actual_rows:
        ids_by_rurality_actual.setdefault(row["ruralLevel"], set()).add(row["id"])

    for rural_level, ids in ids_by_rurality_target.items():
        ids_to_update = ids - ids_by_rurality_actual.get(rural_level, set())
        if ids_to_update:
            educational_models.EducationalInstitution.query.filter(
                educational_models.EducationalInstitution.id.in_(ids_to_update)
            ).update({"ruralLevel": educational_models.InstitutionRuralLevel(rural_level)})

    db.session.commit()


def get_offers_count_for_my_institution(uai: str) -> int:
    offer_query = (
        educational_models.CollectiveOffer.query.join(
            educational_models.EducationalInstitution, educational_models.CollectiveOffer.institution
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            ),
        )
        .filter(educational_models.EducationalInstitution.institutionId == uai)
    )
    offer_count = len([query for query in offer_query if query.isBookable])
    return offer_count


def get_offers_for_my_institution(uai: str) -> BaseQuery:
    return (
        educational_models.CollectiveOffer.query.join(
            educational_models.EducationalInstitution, educational_models.CollectiveOffer.institution
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            ),
            sa.orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(
                offerers_models.Venue.managingOfferer
            ),
            sa.orm.joinedload(educational_models.CollectiveOffer.institution),
            sa.orm.joinedload(educational_models.CollectiveOffer.teacher),
            sa.orm.joinedload(educational_models.CollectiveOffer.nationalProgram),
            sa.orm.joinedload(educational_models.CollectiveOffer.domains),
        )
        .filter(educational_models.EducationalInstitution.institutionId == uai)
    )
