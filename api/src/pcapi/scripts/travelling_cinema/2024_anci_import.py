import csv
from dataclasses import asdict
from dataclasses import dataclass
import logging

from sqlalchemy import func

import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db
from pcapi.routes.serialization import venues_serialize


logger = logging.getLogger(__name__)

DEFAULT_PATH = "/tmp/"


@dataclass
class Accessibility:
    audioDisabilityCompliant: bool
    mentalDisabilityCompliant: bool
    motorDisabilityCompliant: bool
    visualDisabilityCompliant: bool


@dataclass
class VenueRow:
    siren: str
    public_name: str
    name: str
    kind: str
    address: str
    zip_code: str
    city: str
    email: str
    contact_email: str
    siret: str
    description1: str
    description2: str
    latitude: float
    longitude: float
    accessibility: Accessibility


def build_venue_row(row: dict) -> VenueRow:
    if bool(row["Non accessible"]):
        accessibility = Accessibility(
            audioDisabilityCompliant=False,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=False,
            visualDisabilityCompliant=False,
        )
    else:
        accessibility = Accessibility(
            audioDisabilityCompliant=bool(row["Accessibilité - auditif"]),
            mentalDisabilityCompliant=bool(row["Accessibilité - cognitif"]),
            motorDisabilityCompliant=bool(row["Accessibilité - moteur"]),
            visualDisabilityCompliant=bool(row["Accessibilité - visuel"]),
        )

    latitude = row["Lieu latitude"]
    latitude = float(latitude.replace(",", ".")) if latitude else latitude

    longitude = row["Lieu longitude"]
    longitude = float(longitude.replace(",", ".")) if longitude else longitude

    email = row["nouvel Email"]
    if isinstance(email, list):
        email = email[0]
    email = [x.strip() for x in email.split(",")][0]
    email = [x.strip() for x in email.split(" ")][0]
    email = email.replace("'", "").replace('"', "")

    contact_email = row["Email BO"]
    if isinstance(contact_email, list):
        contact_email = contact_email[0]
    contact_email = [x.strip() for x in contact_email.split(",")][0]
    contact_email = [x.strip() for x in contact_email.split(" ")][0]
    contact_email = contact_email.replace("'", "").replace('"', "")

    desc1 = row["Lieu description"].strip()
    desc1 = "" if desc1 == "-" else desc1

    desc2 = row["Lieu description web"]
    desc2 = "" if desc2 == "-" else desc2

    return VenueRow(
        siren=row["Siren"],
        public_name=row["Nom du lieu"],
        name=row["Nom Juridique"],
        kind=row["Type du lieu"],
        address=row["Numéro et voie du lieu"],
        zip_code=row["Code postal"],
        city=row["Ville"],
        email=email,
        contact_email=contact_email,
        siret=None,
        description1=desc1,
        description2=desc2,
        latitude=latitude,
        longitude=longitude,
        accessibility=accessibility,
    )


def get_parsed_rows(path: str) -> list[VenueRow]:
    with open(path, "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        headers = csv_rows.fieldnames
        if not headers:
            print("No header found in csv")
            return []

        try:
            return [build_venue_row(row) for row in csv_rows]
        except KeyError as err:
            print(f"Missing column: {err}")
            return []


def check_csv_input(path: str, full: bool = False) -> bool:
    with open(path, "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        headers = csv_rows.fieldnames
        if not headers:
            print("No header found in csv")
            return False

        if full:
            csv_rows = (row for row in csv_rows)
        else:
            csv_rows = [next(csv_rows)]

        try:
            [build_venue_row(row) for row in csv_rows]
        except KeyError as err:
            print(f"Missing column: {err}")
            return False

        return True


def import_venues_for_travelling_cinema(path: str) -> list[int]:
    row_number_list_error_to_create_venue = []
    venue_ids = []

    with open(path, "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        headers = csv_rows.fieldnames
        if not headers:
            print("No header found in csv")
            return venue_ids

        try:
            rows = [build_venue_row(row) for row in csv_rows]
        except KeyError as err:
            print(f"Missing column: {err}")
            return venue_ids

        for idx, row in enumerate(rows):
            offerer = offerers_models.Offerer.query.filter(offerers_models.Offerer.siren == row.siren).one_or_none()
            if not offerer:
                print("Offerer not found : ", row.siren)
                continue

            try:
                venue = _get_venue(row, offerer)
            except Exception as err:
                print(f"could not get venue: {err} <> name: {row.name}, siren: {row.siren}, offerer: {offerer.id}")
                raise

            if not venue:
                print("creatingVenue : ", row.public_name)
                try:
                    venue = _create_venue(row, offerer)
                    db.session.add(venue)
                except Exception as exc:  # pylint: disable=broad-except
                    row_number_list_error_to_create_venue.append((idx, asdict(row), exc))
                    continue
            else:
                print("VenueAlreadyExists : ", row.public_name)

            venue_ids.append(venue.id)

    if row_number_list_error_to_create_venue:
        from pprint import pprint

        print(f"{len(row_number_list_error_to_create_venue)} error(s) to create venues :")

        for error in row_number_list_error_to_create_venue:
            print(f"\n***** #{error[0]}")
            pprint(error[1])
            print(error[2].__class__.__name__)
            print("*****")

    return venue_ids, row_number_list_error_to_create_venue


def _get_venue(row: VenueRow, offerer: offerers_models.Offerer) -> offerers_models.Venue | None:
    return (
        offerers_models.Venue.query.filter(offerers_models.Venue.managingOffererId == offerer.id)
        .filter(func.lower(offerers_models.Venue.name) == func.lower(row.public_name))
        .one_or_none()
    )


def build_venue_model_data(row: VenueRow) -> dict:
    offerer = offerers_models.Offerer.query.filter(offerers_models.Offerer.siren == row.siren).one_or_none()
    address = _complete_address_and_coordinates_data(row)

    if row.description1 or row.description2:
        comment = f"{row.description1}\n{row.description2}"
    else:
        comment = "Import pass culture"

    return {
        **address,
        "managingOffererId": offerer.id,
        "name": row.name,
        "publicName": row.public_name,
        "venueTypeCode": "TRAVELING_CINEMA" if row.kind == "itinerant" else "MOVIE",
        "bookingEmail": row.email,
        "comment": comment,
        "contact": {
            "email": row.contact_email,
        },
        **asdict(row.accessibility),
    }


def build_venue_model(row: VenueRow) -> venues_serialize.PostVenueBodyModel:
    return venues_serialize.PostVenueBodyModel(**build_venue_model_data(row))


def _create_venue(row: VenueRow, offerer: offerers_models.Offerer) -> offerers_models.Venue:
    address = _complete_address_and_coordinates_data(row)

    if row.description1 or row.description2:
        comment = f"{row.description1}\n{row.description2}"
    else:
        comment = "Import pass culture"

    data = {
        **address,
        "managingOffererId": offerer.id,
        "name": row.name,
        "publicName": row.public_name,
        "venueTypeCode": "TRAVELING_CINEMA" if row.kind == "itinerant" else "MOVIE",
        "bookingEmail": row.email,
        "comment": comment,
        "contact": {
            "email": row.email,
        },
        **asdict(row.accessibility),
    }
    venue = offerers_api.create_venue(venues_serialize.PostVenueBodyModel(**data), None)
    return venue


def _complete_address_and_coordinates_data(row: VenueRow) -> dict:
    return {
        "street": row.address,
        "postalCode": row.zip_code,
        "city": row.city,
        "longitude": row.longitude,
        "latitude": row.latitude,
    }
