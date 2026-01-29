import csv
import datetime
import logging
from io import TextIOWrapper
from typing import Iterable

import click
import schwifty
from flask import Blueprint

from pcapi import settings
from pcapi.connectors.googledrive import GoogleDriveBackend
from pcapi.core.finance import deposit_api
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.providers import models as providers_models
from pcapi.core.users import api as users_api
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.notifications.internal.transactional import import_test_user_failure
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.users import ProUserCreationBodyV2Model
from pcapi.utils import crypto
from pcapi.utils import date as date_utils
from pcapi.utils.email import anonymize_email
from pcapi.utils.email import sanitize_email
from pcapi.utils.siren import complete_siren_or_siret


logger = logging.getLogger(__name__)
blueprint = Blueprint("import_test_users", __name__)


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
    match role:
        case UserRole.UNDERAGE_BENEFICIARY:
            age = 17
        case UserRole.BENEFICIARY:
            age = 18
        case _:
            age = 19
    birth_date = datetime.date(datetime.date.today().year - age, 1, 1)

    user = users_api.create_account(
        email=sanitize_email(row["Mail"]),
        password=_get_password(row),
        birthdate=birth_date,
        is_email_validated=True,
        send_activation_mail=False,
        remote_updates=False,
    )
    user.validatedBirthDate = birth_date
    deposit_api.upsert_deposit(user, "import_test_users (csv)", eligibility=EligibilityType.AGE17_18)
    if role == UserRole.BENEFICIARY:
        user.add_beneficiary_role()
    elif role == UserRole.UNDERAGE_BENEFICIARY:
        user.add_underage_beneficiary_role()
    return user


def _create_pro_user(row: dict) -> User:
    now = date_utils.get_naive_utc_now()

    user = users_api.create_pro_user(
        ProUserCreationBodyV2Model(
            email=row["Mail"],
            first_name=row["Prénom"],
            last_name=row["Nom"],
            password=_get_password(row),
            phone_number=row["Téléphone"],
            contact_ok=False,
            token="token",
        )
    )

    siret = _get_siret(row["SIREN"])
    gps = (48.865987, 2.3232)
    offerer_creation_info = offerers_serialize.CreateOffererQueryModel(
        city="PARIS",
        latitude=gps[0],
        longitude=gps[1],
        name=f"{(row['Type'] or 'test').split(':')[-1].capitalize()} {row['Prénom']} {row['Nom']}",
        postalCode="75001",
        inseeCode="75101",
        siren=siret[:9],
        street="1 place de la Concorde",
        phoneNumber=None,
    )
    new_onboarding_info = offerers_api.NewOnboardingInfo(
        activity=offerers_models.Activity.NOT_ASSIGNED,
        target=offerers_models.Target.INDIVIDUAL_AND_EDUCATIONAL,
        webPresence="https://www.example.com",
    )
    user_offerer = offerers_api.create_offerer(
        user, offerer_creation_info, new_onboarding_info, comment="Créée par la commande `import_test_users`"
    )

    # Validate offerer
    offerer = user_offerer.offerer
    offerer.validationStatus = ValidationStatus.VALIDATED
    offerer.dateValidated = now
    offerer.allowedOnAdage = True
    db.session.add(offerer)

    history_api.add_action(
        history_models.ActionType.OFFERER_VALIDATED,
        author=None,
        user=user,
        offerer=offerer,
        comment="Validée automatiquement par le script de création",
    )

    # Most of offerers are not validated on staging without this commit() - TODO: is this related to atomic? oa?
    db.session.commit()

    address = address_serialize.LocationBodyModel(
        street=offerers_schemas.VenueAddress(offerer_creation_info.street),
        city=offerers_schemas.VenueCity(offerer_creation_info.city),
        postalCode=offerers_schemas.VenuePostalCode(offerer_creation_info.postalCode),
        inseeCode=offerers_schemas.VenueInseeCode("75101"),
        latitude=gps[0],
        longitude=gps[1],
        banId=offerers_schemas.VenueBanId("75101_2259_00001"),  # 1 place de la Concorde
        label=None,
    )

    # TODO(xordoquy): rename address to location ?
    venue_creation_info = venues_serialize.PostVenueBodyModel(
        activity=offerers_models.Activity.OTHER,
        address=address,
        bookingEmail=offerers_schemas.VenueBookingEmail(user.email),
        comment=None,
        culturalDomains=[],
        managingOffererId=offerer.id,
        name=offerers_schemas.VenueName(f"Structure {row['Prénom']} {row['Nom']}"),
        publicName=None,
        siret=offerers_schemas.VenueSiret(siret),
        venueLabelId=None,
        withdrawalDetails=None,
        description=None,
        contact=None,
        audioDisabilityCompliant=False,
        mentalDisabilityCompliant=False,
        motorDisabilityCompliant=False,
        visualDisabilityCompliant=False,
        isOpenToPublic=True,
    )
    venue = offerers_api.create_venue(venue_creation_info, user)
    offerers_api.create_venue_registration(venue.id, new_onboarding_info.target, new_onboarding_info.webPresence)
    venue.adageId = f"TEST{venue.id}"
    venue.adageInscriptionDate = now
    db.session.add(venue)

    for i, status in enumerate(finance_models.BankAccountApplicationStatus, start=1):
        bank_account = finance_models.BankAccount(
            label=f"Compte {i} de {user.firstName} - {status.value}",
            offerer=offerer,
            iban=schwifty.IBAN.generate("FR", bank_code="10010", account_code=f"{siret[:9]}{i:02}").compact,
            dsApplicationId=int(siret) * 100 + i,
            status=status,
        )
        db.session.add(bank_account)
        if status is finance_models.BankAccountApplicationStatus.ACCEPTED:
            db.session.add(offerers_models.VenueBankAccountLink(venue=venue, bankAccount=bank_account, timespan=(now,)))

    # Avoid rollback() on objects above when re-using an existing address in get_or_create_address
    db.session.commit()

    # Create a second address linked to the offerer in another region
    address = offerers_api.get_or_create_address(
        offerers_api.LocationData(
            street="1 Boulevard de la Croisette",
            postal_code="06400",
            city="Cannes",
            latitude=43.551407,
            longitude=7.017984,
            insee_code="06029",
            ban_id="06029_0880_00001",
        ),
        is_manual_edition=False,
    )
    offerers_api.get_or_create_offer_location(offerer.id, address.id, label="Palais des Festivals")

    if row["Type"] in ("externe:bug-bounty", "interne:test"):
        _create_provider(venue, row)

    user.isEmailValidated = True
    user.add_pro_role()

    return user


def _add_or_update_user_from_row(row: dict, update_if_exists: bool) -> User | None:
    user = find_user_by_email(row["Mail"])
    if user and not update_if_exists:
        return None

    if user:
        user.setPassword(_get_password(row))
    else:
        role = UserRole(row["Role"]) if row["Role"] else None
        if role == UserRole.PRO:
            user = _create_pro_user(row)
        else:
            user = _create_beneficiary(row, role)

    user.lastName = row["Nom"]
    user.firstName = row["Prénom"]
    user.phoneNumber = row["Téléphone"]
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
    db.session.add(admin)
    db.session.commit()
    logger.info("Created or updated admin user=%s", admin.id)


def _create_provider(venue: offerers_models.Venue, row: dict) -> None:
    formatted_email = sanitize_email(row["Mail"]).replace("_", "-")
    provider = providers_models.Provider(name=row["Prénom"])
    offerer_provider = offerers_models.OffererProvider(offerer=venue.managingOfferer, provider=provider)
    prefix = f"staging_{formatted_email}"
    key = offerers_models.ApiKey(
        provider=provider,
        prefix=prefix,
        secret=crypto.hash_public_api_key(formatted_email),
    )
    venue_provider = providers_models.VenueProvider(venue=venue, provider=provider)

    db.session.add_all([provider, offerer_provider, key, venue_provider])


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
    except Exception as exc:
        logger.exception("Could not create or update user from Google Drive file", extra={"exc": str(exc)})
        import_test_user_failure.send()
    return []


@blueprint.cli.command("import_test_users")
@click.option(
    "-f",
    "--filename",
    type=str,
    required=False,
    help="Optional path to the CSV file to import (default is from Google Drive)",
)
@click.option("-u", "--update", help="Update users which already exist", is_flag=True)
def import_test_users(filename: str, update: bool) -> None:
    """Creates or updates users listed in a Google Sheet or CSV file"""

    if filename:
        source = filename
        with open(source, encoding="utf-8") as fp:
            new_users = create_users_from_csv(fp)
    else:
        source = settings.IMPORT_USERS_GOOGLE_DOCUMENT_ID
        if not source:
            raise ValueError("IMPORT_USERS_GOOGLE_DOCUMENT_ID is not configured")
        new_users = create_users_from_google_sheet(source, update)

    logger.info("Created or updated %d users from %s", len(new_users), source)
