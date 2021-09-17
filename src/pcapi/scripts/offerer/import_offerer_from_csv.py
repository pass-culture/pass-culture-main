import csv
from datetime import timedelta
import json
from json import JSONDecodeError
import logging

from pcapi.core.offerers.api import create_digital_venue
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueType
from pcapi.core.offerers.repository import find_offerer_by_siren
from pcapi.core.users.api import create_pro_user
from pcapi.core.users.api import create_reset_password_token
from pcapi.domain.password import random_password
from pcapi.models import ApiErrors
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.serialization.users import ProUserCreationBodyModel


logger = logging.getLogger(__name__)


def create_offerer_from_csv(row: dict) -> Offerer:
    offerer = Offerer()
    offerer.name = row["nom_structure"] if row["nom_structure"] else row["Name"]
    offerer.siren = row["SIREN"]
    offerer.address = _get_address_from_row(row)
    offerer.postalCode = _get_postal_code(row)
    offerer.city = row["City"]

    return offerer


def create_venue_from_csv(row: dict, offerer: Offerer) -> Venue:
    venue = Venue(
        address=_get_address_from_row(row),
        postalCode=_get_postal_code(row),
        city=row["commune"],
        departementCode=row["Département"],
        siret=row["SIRET"],
        publicName=row["nom_lieu"],
        bookingEmail=row["Email"],
        venueType=VenueType.query.filter_by(label=row["Catégorie"]).one(),
    )

    if row["nom_lieu"]:
        venue.name = row["nom_lieu"]
    else:
        venue.name = (
            f"Lieu {Venue.query.filter(Venue.siret.startswith(offerer.siren)).count() + 1} - {row['nom_structure']}"
        )
        logger.warning("Venue name missing for offerer with SIREN %s. Génerated name : %s", offerer.siren, venue.name)

    try:
        geoloc = json.loads(row["geoloc"])
        venue.latitude, venue.longitude = geoloc
    except JSONDecodeError:
        pass

    venue.managingOfferer = offerer

    return venue


def _get_address_from_row(row: dict) -> str:
    return row["adresse"].split(",")[0]


def _get_postal_code(row: dict) -> str:
    return row["code_postal"] if row["code_postal"] else row["Postal Code"]


def create_user_model_from_csv(row: dict) -> ProUserCreationBodyModel:
    pro_user_creation_model = ProUserCreationBodyModel(
        email=row["Email"],
        password=random_password(),
        firstName=row["First Name"],
        lastName=row["Last Name"],
        phoneNumber=row["Phone"] if row["Phone"].strip() != "" else "00 00 00 00 00",
        postalCode=_get_postal_code(row),
        city=row["City"],
        publicName=f"{row['First Name']} {row['Last Name']}",
    )

    return pro_user_creation_model


def import_new_offerer_from_csv(row: dict) -> None:
    # We can't process a row without a postal code
    if not row["Postal Code"] and not row["code_postal"]:
        logger.warning("Unable to import this line %s - %s", row[""], row["Company ID"])
        return

    existing_pro = find_user_by_email(row["Email"])
    if existing_pro:
        pro = existing_pro
    else:
        pro_model = create_user_model_from_csv(row)
        pro = create_pro_user(pro_model)
        pro.validationToken = None
        create_reset_password_token(pro, token_life_time=timedelta(days=90))

    existing_offerer = find_offerer_by_siren(row["SIREN"])
    if existing_offerer:
        offerer = existing_offerer
    else:
        offerer = create_offerer_from_csv(row)
        create_digital_venue(offerer)

    offerer.grant_access(pro)

    repository.save(pro)

    if row["SIRET"]:
        venue = create_venue_from_csv(row, offerer)
        try:
            repository.save(venue)
        except ApiErrors:
            logger.warning("Unable to save this venue %s - %s", row[""], row["Company ID"])

    else:
        logger.warning("Unable to import this venue %s - %s", row[""], row["Company ID"])


def import_from_csv_file(csv_file_path: str) -> None:
    with open(csv_file_path) as csv_file:
        csv_reader = csv.dictReader(csv_file)

        for row in csv_reader:
            import_new_offerer_from_csv(row)
