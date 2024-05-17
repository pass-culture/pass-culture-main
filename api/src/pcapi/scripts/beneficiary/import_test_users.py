import csv
import datetime
from io import TextIOWrapper
import logging
from typing import Iterable

import click
from click_option_group import RequiredMutuallyExclusiveOptionGroup
from click_option_group import optgroup
from flask import Blueprint
import schwifty

from pcapi import settings
from pcapi.connectors.googledrive import GoogleDriveBackend
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import api as users_api
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.notifications.internal.transactional import import_test_user_failure
from pcapi.repository import repository
from pcapi.routes.serialization import base as base_serialize
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.users import ProUserCreationBodyV2Model
from pcapi.utils.email import anonymize_email
from pcapi.utils.email import sanitize_email
from pcapi.utils.siren import complete_siren_or_siret


logger = logging.getLogger(__name__)
blueprint = Blueprint("import_test_users", __name__)


def _get_birth_date(row: dict) -> datetime.date:
    return datetime.datetime.strptime(row["Date de naissance"], "%Y-%m-%d").date()


def _get_password(row: dict) -> str:
    if row.get("Mot de passe"):  # Keep compatibility with CSV without this column
        return row["Mot de passe"]
    return settings.TEST_DEFAULT_PASSWORD


def _get_siret(siren: str) -> str:
    # SIREN is CSV file may be incomplete so that a valid one is computed with check digit.
    # SIRET is also calculated as the first valid code with check digit.
    # This is useful for API Entreprise (staging) calls, which require a valid format.
    # Keep compatibility with a full 9-digit SIREN.
    if len(siren) == 8:
        siren = complete_siren_or_siret(siren)
    return complete_siren_or_siret(f"{siren}0001")


def _create_beneficiary(row: dict, role: UserRole | None) -> User:
    user = users_api.create_account(
        email=sanitize_email(row["Mail"]),
        password=_get_password(row),
        birthdate=_get_birth_date(row),
        is_email_validated=True,
        send_activation_mail=False,
        remote_updates=False,
    )
    user.validatedBirthDate = _get_birth_date(row)
    if role == UserRole.BENEFICIARY:
        deposit = finance_api.create_deposit(user, "import_test_users (csv)", eligibility=EligibilityType.AGE18)
        db.session.add(deposit)
        user.add_beneficiary_role()
    elif role == UserRole.UNDERAGE_BENEFICIARY:
        deposit = finance_api.create_deposit(
            user, "import_test_users (csv)", eligibility=EligibilityType.UNDERAGE, age_at_registration=16
        )
        db.session.add(deposit)
        user.add_underage_beneficiary_role()
    return user


def _create_pro_user(row: dict) -> User:
    user = users_api.create_pro_user(
        ProUserCreationBodyV2Model(  # type: ignore [call-arg]
            email=row["Mail"],
            firstName=row["Prénom"],
            lastName=row["Nom"],
            password=_get_password(row),
            phoneNumber=row["Téléphone"],
            contactOk=False,
            token="token",
        )
    )

    siret = _get_siret(row["SIREN"])
    offerer_creation_info = offerers_serialize.CreateOffererQueryModel(
        city="MA VILLE",
        latitude=46.126,
        longitude=-3.033,
        name=f'Structure {row["Nom"]}',
        postalCode=row["Code postal"],
        siren=siret[:9],
        street="1 avenue de la Culture",
    )
    new_onboarding_info = offerers_api.NewOnboardingInfo(
        target=offerers_models.Target.INDIVIDUAL_AND_EDUCATIONAL,
        venueTypeCode=offerers_models.VenueTypeCode.ADMINISTRATIVE.name,
        webPresence="https://www.example.com",
    )
    user_offerer = offerers_api.create_offerer(
        user, offerer_creation_info, new_onboarding_info, comment="Créée par la commande `import_test_users`"
    )

    # Validate offerer
    offerer = user_offerer.offerer
    offerer.validationStatus = ValidationStatus.VALIDATED
    offerer.dateValidated = datetime.datetime.utcnow()
    db.session.add(offerer)

    history_api.add_action(
        history_models.ActionType.OFFERER_VALIDATED,
        None,
        user=user,
        offerer=offerer,
        comment="Validée automatiquement par le script de création",
    )

    venue_creation_info = venues_serialize.PostVenueBodyModel(
        street=base_serialize.VenueAddress(offerer_creation_info.street),
        banId=None,
        bookingEmail=base_serialize.VenueBookingEmail(user.email),
        city=base_serialize.VenueCity(offerer_creation_info.city),
        comment=None,
        latitude=46.126,
        longitude=-3.033,
        managingOffererId=offerer.id,
        name=base_serialize.VenueName(f'Lieu {row["Nom"]}'),
        publicName=None,
        postalCode=row["Code postal"],
        siret=base_serialize.VenueSiret(siret),
        venueLabelId=None,
        venueTypeCode=offerers_models.VenueTypeCode.ADMINISTRATIVE.name,
        withdrawalDetails=None,
        description=None,
        contact=None,
        audioDisabilityCompliant=False,
        mentalDisabilityCompliant=False,
        motorDisabilityCompliant=False,
        visualDisabilityCompliant=False,
    )
    venue = offerers_api.create_venue(venue_creation_info)
    offerers_api.create_venue_registration(venue.id, new_onboarding_info.target, new_onboarding_info.webPresence)

    for i, status in enumerate(finance_models.BankAccountApplicationStatus, start=1):
        bank_account = finance_models.BankAccount(
            label=f"Compte {i} de {user.firstName} - {status.value}",
            offerer=offerer,
            iban=schwifty.IBAN.generate("FR", bank_code="10010", account_code=f"{siret[:9]}{i:02}").compact,
            bic="BDFEFRPP",
            dsApplicationId=int(siret) * 100 + i,
            status=status,
        )
        db.session.add(bank_account)
        if status is finance_models.BankAccountApplicationStatus.ACCEPTED:
            db.session.add(
                offerers_models.VenueBankAccountLink(
                    venue=venue, bankAccount=bank_account, timespan=(datetime.datetime.utcnow(),)
                )
            )

    user.isEmailValidated = True
    user.add_pro_role()

    return user


def _add_or_update_user_from_row(row: dict, update_if_exists: bool) -> User | None:
    user = find_user_by_email(row["Mail"])
    if user and not update_if_exists:
        return None

    if user:
        user.dateOfBirth = _get_birth_date(row)
        user.setPassword(_get_password(row))
    else:
        role = UserRole(row["Role"]) if row["Role"] else None
        if role == UserRole.PRO:
            user = _create_pro_user(row)
        else:
            user = _create_beneficiary(row, role)

    user.lastName = row["Nom"]
    user.firstName = row["Prénom"]
    user.phoneNumber = row["Téléphone"]  # type: ignore [method-assign]
    user.departementCode = row["Département"]
    user.postalCode = row["Code postal"]
    user.comment = row["Type"]
    user.add_test_role()
    db.session.add(user)
    db.session.commit()

    anonymized_email = anonymize_email(email=user.email)

    logger.info(
        "Created or updated user=%s <%s> %s from CSV import",
        user.id,
        anonymized_email,
        [role.value for role in user.roles],
    )

    return user


def _add_or_update_admin(update_if_exists: bool) -> None:
    admin = find_user_by_email("admin@example.com")
    if admin and not update_if_exists:
        return
    if not admin:
        admin = users_api.create_account(
            email="admin@example.com",
            password=settings.TEST_DEFAULT_PASSWORD,
            birthdate=datetime.date(1946, 12, 24),
            is_email_validated=True,
            send_activation_mail=False,
            remote_updates=False,
        )
    admin.setPassword(settings.TEST_DEFAULT_PASSWORD)
    admin.remove_beneficiary_role()
    admin.add_admin_role()
    admin.firstName = "Jeanne"
    admin.lastName = "Admin"
    repository.save(admin)
    logger.info("Created or updated admin user=%s", admin.id)


def create_or_update_users(rows: Iterable[dict], update_if_exists: bool = False) -> list[User]:
    # The purpose of this function is to recreate test users on
    # staging after the staging database is reset. It's not meant to
    # be used anywhere else, and certainly not on production.
    if not settings.ENABLE_IMPORT_TEST_USERS:
        raise ValueError("This function is not supposed to be run on production")

    users = []
    for row in rows:
        user = _add_or_update_user_from_row(row, update_if_exists)
        if user:
            users.append(user)

    _add_or_update_admin(update_if_exists)

    return users


def create_users_from_csv(csv_file: TextIOWrapper, update_if_exists: bool = False) -> list[User]:
    csv_reader = csv.DictReader(csv_file)
    return create_or_update_users(csv_reader, update_if_exists=update_if_exists)


def create_users_from_google_sheet(document_id: str, update_if_exists: bool = False) -> list[User]:
    # Replace "/edit" with "/export?format=csv" in Google Drive URL to get CSV file
    backend = GoogleDriveBackend()
    content = backend.download_file(document_id, "text/csv")
    wrapper = TextIOWrapper(content, encoding="utf-8")
    try:
        return create_users_from_csv(wrapper, update_if_exists=update_if_exists)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Could not create or update user from Google Drive file", extra={"exc": str(exc)})
        import_test_user_failure.send()
    return []


@blueprint.cli.command("import_test_users")
@optgroup.group("User data sources", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option(
    "-d",
    "--default",
    is_flag=True,
    default=False,
    help="Import from default Google document set in IMPORT_USERS_GOOGLE_DOCUMENT_ID",
)
@optgroup.option("-f", "--filename", help="Path to the CSV file to import")
@optgroup.option("-g", "--google", "google_id", help="Google document id")
@click.option("-u", "--update", help="Update users which already exist", is_flag=True, default=False)
def import_test_users(default: bool, filename: str, google_id: str, update: bool) -> None:
    """Creates or updates users listed in a Google Sheet or CSV file"""

    if filename:
        source = filename
        with open(source, encoding="utf-8") as fp:
            new_users = create_users_from_csv(fp)
    else:
        if google_id:
            source = google_id
        else:
            source = settings.IMPORT_USERS_GOOGLE_DOCUMENT_ID
            if not source:
                raise ValueError("IMPORT_USERS_GOOGLE_DOCUMENT_ID is not configured")
        new_users = create_users_from_google_sheet(source, update)

    logger.info("Created or updated %d users from %s", len(new_users), source)
