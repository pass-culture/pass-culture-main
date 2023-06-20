import csv
import logging

from sqlalchemy import func

import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
from pcapi.core.providers import models as providers_models
import pcapi.core.providers.api as providers_api
from pcapi.models import db
from pcapi.routes.serialization import venues_serialize
from pcapi.utils import requests


logger = logging.getLogger(__name__)

DEFAULT_PATH = "/tmp/"

expected_headers = {
    "Siren",
    "PublicName",
    "VenueName",
    "VenueType",
    "Adresse",
    "ZipCode",
    "City",
    "Email",
    "Siret",
    "VenueDescription1",
    "VenueDescription2",
    "VenueLatitude",
    "VenueLongitude",
    "Visuel",
    "Cognitif",
    "Moteur",
    "Auditif",
    "NonAccessible",
}


def import_venues_for_travelling_cinema(file_name: str, provider_id: int, file_path: str = DEFAULT_PATH) -> None:
    row_number_list_error_to_create_venue = []

    provider = get_provider_by_id(provider_id)
    if not provider:
        print("No provider found")
        return
    print("Provider found : ", provider.name, provider.id)

    with open(f"{file_path}{file_name}", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        headers = csv_rows.fieldnames
        if not headers:
            print("No header found in csv")
            return
        if not expected_headers.issubset(headers):
            print("Missing fields in csv file", expected_headers - set(headers))
            return

        for row in csv_rows:
            offerer = offerers_models.Offerer.query.filter(offerers_models.Offerer.siren == row["Siren"]).one_or_none()
            if not offerer:
                print("Offerer not found : ", row["Siren"])
                continue

            venue = _get_venue(row, offerer)
            if not venue:
                print("creatingVenue : ", row["PublicName"])
                try:
                    venue = _create_venue(row, offerer)
                    db.session.add(venue)
                except Exception as exc:  # pylint: disable=broad-except
                    row_number_list_error_to_create_venue.append((row["PublicName"], exc))
                    continue
            else:
                print("VenueAlreadyExists : ", row["PublicName"])

            if not any(venueProvider.providerId == provider_id for venueProvider in venue.venueProviders):
                print("creatingVenueProvider", row["PublicName"])
                providers_api.connect_venue_to_provider(venue, provider)
            else:
                print("VenueProviderAlreadyExists : ", row["PublicName"])

    if row_number_list_error_to_create_venue:
        print(
            f"{len(row_number_list_error_to_create_venue)} error(s) to create venues :"
            f"{row_number_list_error_to_create_venue}"
        )


def get_provider_by_id(provider_id: int) -> providers_models.Provider | None:
    return providers_models.Provider.query.filter_by(id=provider_id).one_or_none()


def _get_venue(row: dict, offerer: offerers_models.Offerer) -> offerers_models.Venue | None:
    return (
        offerers_models.Venue.query.filter(offerers_models.Venue.managingOffererId == offerer.id)
        .filter(func.lower(offerers_models.Venue.name) == func.lower(row["VenueName"]))
        .one_or_none()
    )


def _create_venue(row: dict, offerer: offerers_models.Offerer) -> offerers_models.Venue:
    adress = _complete_address_and_coordinates_data(row)
    accessibility = handle_accessibility(row)
    comment = row["VenueDescription1"] + "\n" + row["VenueDescription2"]
    if not comment:
        comment = "Import pass culture"
    data = {
        **adress,
        "managingOffererId": offerer.id,
        "name": row["VenueName"],
        "publicName": row["PublicName"],
        "venueTypeCode": "TRAVELING_CINEMA" if row["VenueType"] == "itinerant" else "MOVIE",
        "bookingEmail": row["Email"],
        "comment": comment,
        "contact": {
            "email": row["Email"],
        },
        **accessibility,
    }
    venue = offerers_api.create_venue(venues_serialize.PostVenueBodyModel(**data))
    return venue


def handle_accessibility(row: dict) -> dict:
    if row["NonAccessible"] == 1:
        return {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
    return {
        "audioDisabilityCompliant": bool(row["Auditif"]),
        "mentalDisabilityCompliant": bool(row["Cognitif"]),
        "motorDisabilityCompliant": bool(row["Moteur"]),
        "visualDisabilityCompliant": bool(row["Visuel"]),
    }


def _complete_address_and_coordinates_data(infos: dict) -> dict:
    street = infos["Adresse"]
    zip_code = infos["ZipCode"]
    city = infos["City"]
    longitude = infos["VenueLatitude"].replace(",", ".")
    latitude = infos["VenueLongitude"].replace(",", ".")
    if street and zip_code and city:
        longitude, latitude = _get_longitude_and_latitude_from_address(street, zip_code, city)
    else:
        if longitude and latitude:
            street, zip_code, city = _get_address_from_longitude_and_latitude(longitude=longitude, latitude=latitude)

    return {
        "address": street,
        "postalCode": zip_code,
        "city": city,
        "longitude": longitude,
        "latitude": latitude,
    }


def _get_longitude_and_latitude_from_address(street: str, zip_code: str, city: str) -> tuple[float, float]:
    address = f"{street} {zip_code} {city}"

    url = f"https://api-adresse.data.gouv.fr/search/?limit=1&q={address}"
    try:
        response = requests.get(url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as exc:
        logger.exception("Failed to get data from api-adresse.data.gouv.fr", extra={"address": address})
        raise Exception(  # pylint: disable=broad-exception-raised
            "ERR : Error getting API adresse for address : {}".format(address)
        ) from exc

    if response.status_code != 200:
        raise Exception(  # pylint: disable=broad-exception-raised
            "ERR : Error getting API adresse for adress : {}".format(address)
        )

    data = response.json()
    geometry = data["features"][0]["geometry"]
    longitude = geometry["coordinates"][0]
    latitude = geometry["coordinates"][1]

    return float(longitude), float(latitude)


def _get_address_from_longitude_and_latitude(longitude: float, latitude: float) -> tuple[str, str, str]:
    url = f"https://api-adresse.data.gouv.fr/reverse/?lon={longitude}&lat={latitude}"
    try:
        response = requests.get(url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as exc:
        logger.exception("Failed to get data from api-adresse.data.gouv.fr", extra={"lon": longitude, "lat": latitude})
        raise Exception(  # pylint: disable=broad-exception-raised
            "ERR : Error getting API adresse for lon, lat : {} {}".format(longitude, latitude)
        ) from exc

    if response.status_code != 200:
        raise Exception(  # pylint: disable=broad-exception-raised
            "ERR : Error getting API adresse for lon, lat : {} {}".format(longitude, latitude)
        )

    data = response.json()
    properties = data["features"][0]["properties"]
    street = properties["name"]
    zip_code = properties["postcode"]
    city = properties["city"]

    return street, zip_code, city
