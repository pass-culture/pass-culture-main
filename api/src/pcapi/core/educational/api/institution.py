import csv
import logging
import os
import typing
from datetime import datetime
from decimal import Decimal

from sqlalchemy import orm as sa_orm

from pcapi.connectors.big_query.queries import InstitutionRuralLevelQuery
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational.adage_backends.serialize import AdageEducationalInstitution
from pcapi.core.educational.constants import INSTITUTION_TYPES
from pcapi.models import db
from pcapi.utils import db as db_utils
from pcapi.utils import postal_code as postal_code_utils


logger = logging.getLogger(__name__)


def get_all_educational_institutions(page: int, per_page_limit: int) -> tuple[list, int]:
    offset = (per_page_limit * (page - 1)) if page > 0 else 0
    return repository.get_all_educational_institutions(offset=offset, limit=per_page_limit)


def get_educational_institution_department_code(institution: models.EducationalInstitution) -> str:
    department_code = postal_code_utils.PostalCode(institution.postalCode).get_departement_code()
    return department_code


def search_educational_institution(
    *,
    educational_institution_id: int | None,
    name: str | None,
    institution_type: str | None,
    city: str | None,
    postal_code: str | None,
    limit: int,
    uai: str | None,
) -> list[models.EducationalInstitution]:
    return repository.search_educational_institution(
        educational_institution_id=educational_institution_id,
        name=name,
        city=city,
        postal_code=postal_code,
        institution_type=institution_type,
        limit=limit,
        uai=uai,
    )


def import_deposit_institution_csv(
    *, path: str, year: int, ministry: str, conflict: str, final: bool, program_name: str | None
) -> Decimal:
    """
    Import deposits from csv file and update institutions according to adage data
    Return the total imported amount
    """

    if not os.path.exists(path):
        raise ValueError("The given file does not exist")

    try:
        educational_year = repository.get_educational_year_beginning_at_given_year(year)
    except exceptions.EducationalYearNotFound:
        raise ValueError(f"Educational year not found for year {year}")

    with open(path, "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        headers = csv_rows.fieldnames
        if not headers or ("UAICode" not in headers and "UAI" not in headers):
            raise ValueError("UAICode or depositAmount missing in CSV headers")

        data: dict[str, Decimal] = {}
        # sometimes we get 1 row per institution and sometimes 1 row per class.
        for row in csv_rows:
            # try to get the UAI
            uai_header = "UAI" if "UAI" in headers else "UAICode"
            uai = row[uai_header].strip()
            # try to get the amount
            if "Crédits de dépenses" in headers or "depositAmount" in headers:
                amount_header = "depositAmount" if "depositAmount" in headers else "Crédits de dépenses"
                amount = Decimal(row[amount_header])
            elif "montant par élève" in headers and "Effectif" in headers:
                amount = Decimal(row["Effectif"]) * Decimal(row["montant par élève"])
            else:
                raise ValueError("Now way to get the amount found")

            if uai in data:
                data[uai] += amount
            else:
                data[uai] = amount

        logger.info("Finished reading data from csv, starting deposit import")
        total_amount = import_deposit_institution_data(
            data=data,
            educational_year=educational_year,
            ministry=models.Ministry[ministry],
            conflict=conflict,
            final=final,
        )

        if program_name is not None:
            educational_program = (
                db.session.query(models.EducationalInstitutionProgram).filter_by(name=program_name).one()
            )
            logger.info("Updating institutions with program %s", program_name)
            _update_institutions_educational_program(
                educational_program=educational_program, uais=data.keys(), start=educational_year.beginningDate
            )

        return total_amount


def import_deposit_institution_data(
    *,
    data: dict[str, Decimal],
    educational_year: models.EducationalYear,
    ministry: models.Ministry,
    final: bool,
    conflict: str,
) -> Decimal:
    adage_institutions = {
        i.uai: i for i in adage_client.get_adage_educational_institutions(ansco=educational_year.adageId)
    }
    db_institutions = {
        institution.institutionId: institution for institution in db.session.query(models.EducationalInstitution).all()
    }

    not_found_uais = [uai for uai in data if uai not in adage_institutions]
    if not_found_uais:
        raise ValueError(f"UAIs not found in adage: {not_found_uais}")

    total_amount = Decimal(0)
    for uai, amount in data.items():
        created = False
        adage_institution = adage_institutions[uai]
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
            logger.warning("UAI:%s not found in db, creating institution", uai)
            db_institution = models.EducationalInstitution(
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
            deposit = (
                db.session.query(models.EducationalDeposit)
                .filter(
                    models.EducationalDeposit.educationalYearId == educational_year.adageId,
                    models.EducationalDeposit.educationalInstitutionId == db_institution.id,
                )
                .one_or_none()
            )

        if deposit:
            if deposit.ministry != ministry and conflict == "replace":
                logger.warning(
                    "Ministry changed from '%s' to '%s' for deposit %s",
                    deposit.ministry.name,
                    ministry.name,
                    deposit.id,
                )
                deposit.ministry = ministry
            deposit.amount = amount
            deposit.isFinal = final
        else:
            deposit = models.EducationalDeposit(
                educationalYear=educational_year,
                educationalInstitution=db_institution,
                amount=amount,
                ministry=ministry,
                isFinal=final,
            )
            db.session.add(deposit)

        total_amount += amount

    db.session.flush()
    return total_amount


def _update_institutions_educational_program(
    educational_program: models.EducationalInstitutionProgram, uais: typing.Iterable[str], start: datetime
) -> None:
    """
    For now we do not manage the specific cases:
    - an institution is currently linked to the program, but it is not present in the deposit data (i.e not present in uais)
    - an institution was previously linked to the program and it is present in the deposit data
    In both cases we log an error

    For an institution that was never linked to the program, we simply add the link
    """
    institutions: list[models.EducationalInstitution] = (
        db.session.query(models.EducationalInstitution)
        .options(sa_orm.joinedload(models.EducationalInstitution.programAssociations))
        .all()
    )

    institution_by_uai = {institution.institutionId: institution for institution in institutions}

    institutions_in_program_not_in_data = {
        institution.institutionId
        for institution in institutions
        if institution.institutionId not in uais
        and institution.programAssociations
        and start in institution.programAssociations[0].timespan
    }
    if institutions_in_program_not_in_data:
        logger.error(
            "UAIs in DB are associated with program %s but not present in data: %s",
            educational_program.name,
            ", ".join(institutions_in_program_not_in_data),
        )

    for uai in uais:
        institution = institution_by_uai[uai]
        program_associations = [
            association
            for association in institution.programAssociations
            if association.programId == educational_program.id
        ]
        if program_associations:
            [association] = institution.programAssociations
        else:
            association = None

        if association is None:
            logger.info("Linking UAI %s to program %s", uai, educational_program.name)
            institution.programAssociations.append(
                models.EducationalInstitutionProgramAssociation(
                    programId=educational_program.id,
                    timespan=db_utils.make_timerange(start, None),
                )
            )
        elif association.timespan.upper is not None and association.timespan.upper < start:
            logger.error(
                "UAI %s was previously associated with program %s, cannot add it back", uai, educational_program.name
            )

    db.session.flush()


def get_current_year_remaining_credit(institution: models.EducationalInstitution) -> Decimal:
    """Return the institution's remaining credit for the current year.
    The computation stays the same whether the deposit is final or not:

      current year deposit amount - sum of confirmed bookings amounts
    """
    educational_year = repository.find_educational_year_by_date(datetime.utcnow())
    assert educational_year is not None

    deposit = repository.find_educational_deposit_by_institution_id_and_year(institution.id, educational_year.adageId)
    if deposit is None:
        return Decimal(0)

    spent_amount = repository.get_confirmed_collective_bookings_amount(institution.id, educational_year.adageId)

    return deposit.amount - spent_amount


def create_missing_educational_institution_from_adage(destination_uai: str) -> models.EducationalInstitution:
    """
    Fetch known adage institutions of the current year and create the
    missing institution inside or database if the target uai exists.
    """
    year = repository.find_educational_year_by_date(datetime.utcnow())
    if year is None:
        raise exceptions.EducationalYearNotFound()

    adage_institutions = adage_client.get_adage_educational_institutions(year.adageId)
    if not adage_institutions:
        raise exceptions.NoAdageInstitution()

    try:
        adage_institution = next(
            adage_institution for adage_institution in adage_institutions if adage_institution.uai == destination_uai
        )
    except StopIteration:
        raise exceptions.MissingAdageInstitution()
    return create_educational_institution_from_adage(adage_institution)


def create_educational_institution_from_adage(
    institution: AdageEducationalInstitution,
) -> models.EducationalInstitution:
    educational_institution = models.EducationalInstitution(
        institutionId=institution.uai,
        institutionType=institution.sigle,
        name=institution.libelle,
        city=institution.communeLibelle,
        postalCode=institution.codePostal,
        email=institution.courriel or "",
        phoneNumber=institution.telephone or "",
        isActive=True,
    )

    db.session.add(educational_institution)
    db.session.flush()
    return educational_institution


def synchronise_institutions_geolocation(adage_year_id: str | None = None) -> None:
    if adage_year_id is None:
        year = repository.find_educational_year_by_date(datetime.utcnow())
        if year is None:
            raise exceptions.EducationalYearNotFound()
        adage_year_id = year.adageId

    adage_institutions = adage_client.get_adage_educational_institutions(adage_year_id)
    adage_uais = [instition.uai for instition in adage_institutions]

    educational_institutions = (
        db.session.query(models.EducationalInstitution)
        .filter(models.EducationalInstitution.institutionId.in_(adage_uais))
        .all()
    )
    educational_institutions_by_uai = {
        institution.institutionId: institution for institution in educational_institutions
    }

    for adage_institution in adage_institutions:
        educational_institution = educational_institutions_by_uai.get(adage_institution.uai)
        if educational_institution:
            educational_institution.latitude = adage_institution.latitude
            educational_institution.longitude = adage_institution.longitude
            db.session.add(educational_institution)
    db.session.flush()


def synchronise_rurality_level() -> None:
    rows = list(InstitutionRuralLevelQuery().execute())
    actual_rows = (
        e._asdict()
        for e in db.session.query(models.EducationalInstitution).with_entities(
            models.EducationalInstitution.id, models.EducationalInstitution.ruralLevel
        )
    )

    ids_by_rurality_target: dict[int, set[models.InstitutionRuralLevel]] = {}
    for row in rows:
        ids_by_rurality_target.setdefault(row.institution_rural_level, set()).add(row.institution_id)

    ids_by_rurality_actual: dict[int, set[models.InstitutionRuralLevel]] = {}
    for row in actual_rows:
        ids_by_rurality_actual.setdefault(row["ruralLevel"], set()).add(row["id"])

    for rural_level, ids in ids_by_rurality_target.items():
        ids_to_update = ids - ids_by_rurality_actual.get(rural_level, set())
        rural_level_enum = models.InstitutionRuralLevel(rural_level) if rural_level else None
        if ids_to_update:
            db.session.query(models.EducationalInstitution).filter(
                models.EducationalInstitution.id.in_(ids_to_update)
            ).update({"ruralLevel": rural_level_enum})

    db.session.commit()


def get_offers_count_for_my_institution(uai: str) -> int:
    offer_query: "sa_orm.Query[models.CollectiveOffer]" = (
        db.session.query(models.CollectiveOffer)
        .join(models.EducationalInstitution, models.CollectiveOffer.institution)
        .options(
            sa_orm.joinedload(models.CollectiveOffer.collectiveStock).joinedload(
                models.CollectiveStock.collectiveBookings
            ),
        )
        .filter(models.EducationalInstitution.institutionId == uai)
    )
    offer_count = len([offer for offer in offer_query if offer.isBookable])
    return offer_count


def get_playlist_max_distance(institution: models.EducationalInstitution) -> int:
    return models.PLAYLIST_RURALITY_MAX_DISTANCE_MAPPING.get(institution.ruralLevel, 60)
