import csv
import datetime
import decimal
import functools
import logging
from collections.abc import Iterable
from io import TextIOWrapper
from secrets import token_urlsafe

import click
import schwifty
from flask import Blueprint

from pcapi import settings
from pcapi.connectors.googledrive import GoogleDriveBackend
from pcapi.core import search
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.external.zendesk_sell import api as zendesk_sell_api
from pcapi.core.finance import deposit_api
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import constants as history_constants
from pcapi.core.internal_notifications.transactional import import_test_user_failure
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.providers import models as providers_models
from pcapi.core.search.models import IndexationReason
from pcapi.core.users import api as users_api
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.serialization.users import ProUserCreationBodyV2Model
from pcapi.utils import crypto
from pcapi.utils import date as date_utils
from pcapi.utils.email import anonymize_email
from pcapi.utils.email import sanitize_email
from pcapi.utils.siren import complete_siren_or_siret
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import on_commit


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
    siren = siret[:9]
    offerer = db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.siren == siren).one_or_none()

    if offerer is None:
        # create the offerer
        offerer = offerers_models.Offerer(
            name=f"{(row['Type'] or 'test').split(':')[-1].capitalize()} {row['Prénom']} {row['Nom']}",
            siren=siren,
            isActive=True,
            validationStatus=ValidationStatus.VALIDATED,
            dateValidated=now,
            allowedOnAdage=True,
        )
        db.session.add(offerer)
        history_api.add_action(
            history_constants.ActionType.OFFERER_NEW,
            author=user,
            user=user,
            offerer=offerer,
            comment="Créée par la commande `import_test_users`",
        )
        db.session.flush()

    # create the user_offerer
    user_offerer = offerers_models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.VALIDATED)
    db.session.add(user_offerer)
    history_api.add_action(
        history_constants.ActionType.USER_OFFERER_NEW,
        author=user,
        user=user,
        offerer=offerer,
        comment="Créée par la commande `import_test_users`",
    )
    history_api.add_action(
        history_constants.ActionType.OFFERER_VALIDATED,
        author=None,
        user=user,
        offerer=offerer,
        comment="Validée automatiquement par le script de création",
    )
    db.session.flush()

    # user and offerer side effects
    external_attributes_api.update_external_pro(user.email)
    zendesk_sell_api.create_offerer(offerer)

    # create the venue
    dms_token = offerers_api.generate_dms_token()
    name = f"Structure {row['Prénom']} {row['Nom']}"
    venue = offerers_models.Venue(
        dmsToken=dms_token,
        activity=offerers_models.Activity.OTHER,
        venueTypeCode=offerers_schemas.VenueTypeCode.OTHER,
        bookingEmail=user.email,
        comment=None,
        managingOffererId=offerer.id,
        name=name,
        publicName=name,
        siret=siret,
        venueLabelId=None,
        withdrawalDetails=None,
        description=None,
        audioDisabilityCompliant=False,
        mentalDisabilityCompliant=False,
        motorDisabilityCompliant=False,
        visualDisabilityCompliant=False,
        isOpenToPublic=True,
        isPermanent=True,
        validationStatus=offerers_models.VenueValidationStatus.APPROVED,
    )
    db.session.add(venue)
    history_api.add_action(history_constants.ActionType.VENUE_CREATED, author=user, venue=venue)
    db.session.flush()

    # venue side effects
    on_commit(functools.partial(search.async_index_venue_ids, [venue.id], reason=IndexationReason.VENUE_CREATION))
    zendesk_sell_api.create_venue(venue)

    venue.adageId = f"TEST{venue.id}"
    venue.adageInscriptionDate = now

    # create the venue address
    address_body = offerers_schemas.CoreLocationModelV2(
        isManualEdition=False,
        isVenueLocation=True,
        banId="75101_2259_00001",
        city="PARIS",
        inseeCode="75101",
        label=None,
        latitude=decimal.Decimal("48.865987"),
        longitude=decimal.Decimal("2.3232"),
        postalCode="75001",
        street="1 place de la Concorde",
    )

    address = offerers_api.create_offerer_address_from_address_api(address_body)
    offerer_address = offerers_models.OffererAddress(
        addressId=address.id,
        type=offerers_models.LocationType.VENUE_LOCATION,
        label=None,  # venue location always gets an empty label
        venue=venue,
    )
    db.session.add(offerer_address)
    db.session.flush()

    # create finance objects
    offerers_api.link_venue_to_pricing_point(venue, pricing_point_id=venue.id)

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

    db.session.flush()

    # Create a second address linked to the offerer in another region
    second_address = offerers_api.get_or_create_address(
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
    offerers_api.get_or_create_offer_location(
        venue_id=venue.id,
        address_id=second_address.id,
        label="Palais des Festivals",
    )

    if row["Type"] in ("externe:bug-bounty", "interne:test"):
        _create_provider(venue, row)

    user.isEmailValidated = True
    user.add_pro_role()
    db.session.flush()

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
            with atomic():
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
    provider = providers_models.Provider(name=row["Prénom"], hmacKey=token_urlsafe(64))
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
