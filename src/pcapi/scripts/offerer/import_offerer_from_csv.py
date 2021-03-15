import ast
import csv
from typing import Dict

from pcapi.core.offerers.api import create_digital_venue
from pcapi.core.offerers.models import Venue
from pcapi.core.users.api import create_pro_user
from pcapi.models import Offerer
from pcapi.models import VenueType
from pcapi.repository import repository
from pcapi.repository.offerer_queries import find_by_siren
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.serialization.users import ProUserCreationBodyModel
from pcapi.utils.logger import json_logger


def create_offerer_from_csv(row: Dict) -> Offerer:
    offerer = Offerer()
    offerer.name = row["nom_structure"] if row["nom_structure"] else row["Name"]
    offerer.siren = row["SIREN"]
    offerer.address = row["adresse"].split(",")[0]
    offerer.postalCode = _get_postal_code(row)
    offerer.city = row["City"]

    return offerer


def create_venue_from_csv(row: Dict, offerer_siren: str) -> Venue:
    venue = Venue(
        address=row["adresse"].split(",")[0],
        postalCode=_get_postal_code(row),
        city=row["commune"],
        departementCode=row["Département"],
        siret=row["SIRET"].replace(".0", ""),
        publicName=row["nom_lieu"],
        bookingEmail=row["Email"],
        venueType=VenueType.query.filter_by(label=row["Catégorie"]).first(),
    )

    if row["nom_lieu"]:
        venue.name = row["nom_lieu"]
    else:
        venue.name = (
            f"Lieu {Venue.query.filter(Venue.siret.startswith(offerer_siren)).count() + 1} - {row['nom_structure']}"
        )

    try:
        geoloc = ast.literal_eval(row["geoloc"])
        venue.latitude = geoloc[0]
        venue.longitude = geoloc[1]
    except SyntaxError:
        pass

    return venue


def _get_postal_code(row):
    return row["code_postal"] if row["code_postal"] else row["Postal Code"]


def create_user_model_from_csv(row: Dict) -> ProUserCreationBodyModel:
    pro_user_creation_model = ProUserCreationBodyModel(
        email=row["Email"],
        password="Azerty@123456",
        firstName=row["First Name"],
        lastName=row["Last Name"],
        phoneNumber=row["Phone"],
        postalCode=_get_postal_code(row),
        city=row["City"],
        publicName=f"{row['First Name']} {row['Last Name']}",
    )

    return pro_user_creation_model


def import_new_offerer_from_csv(row: Dict):
    # We can't process a row without a postal code
    if not row["Postal Code"] and not row["code_postal"]:
        json_logger.warning("Unable to import this line %s - %s", row[""], row["Company ID"])
        return

    existing_pro = find_user_by_email(row["Email"])
    if existing_pro:
        pro = existing_pro
    else:
        pro_model = create_user_model_from_csv(row)
        pro = create_pro_user(pro_model)

    existing_offerer = find_by_siren(row["SIREN"])
    if existing_offerer:
        offerer = existing_offerer
    else:
        offerer = create_offerer_from_csv(row)
        create_digital_venue(offerer)

    offerer.grant_access(pro)

    if pro.departementCode:
        repository.save(pro)

    if row["SIRET"]:
        venue = create_venue_from_csv(row, offerer.siren)
        venue.managingOfferer = offerer
        repository.save(venue)
    else:
        json_logger.warning("Unable to import this venue %s - %s", row[""], row["Company ID"])


def import_from_csv_file(csv_file_path: str) -> None:
    csv_file = open(csv_file_path)
    csv_reader = csv.DictReader(csv_file)

    for row in csv_reader:
        import_new_offerer_from_csv(row)
