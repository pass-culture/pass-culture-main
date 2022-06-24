import csv
import datetime
import logging
from typing import Optional

from sqlalchemy import func

from pcapi.connectors.api_entreprises import ApiEntrepriseException
from pcapi.core.categories import subcategories
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models
from pcapi.routes.serialization import offers_serialize
from pcapi.routes.serialization import stock_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.utils import requests
from pcapi.utils.date import get_department_timezone
from pcapi.utils.date import local_datetime_to_default_timezone
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)

DEFAULT_PATH = "/tmp/"


def _is_header_or_blank_row(row: list[str]) -> bool:
    return not row or not row[0] or row[0] == "Identifiant du compte (SIREN)"


def get_longitude_and_latitude_from_address(street: str, zip_code: str, city: str) -> tuple[float, float]:
    address = f"{street} {zip_code} {city}"

    url = f"https://api-adresse.data.gouv.fr/search/?limit=1&q={address}"
    try:
        response = requests.get(url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as exc:
        logger.exception("Failed to get data from api-adresse.data.gouv.fr", extra={"address": address})
        raise ApiEntrepriseException("Error getting API adresse for adresse : {}".format(address)) from exc

    if response.status_code != 200:
        raise ApiEntrepriseException("Error getting API adresse for adresse : {}".format(address))

    data = response.json()
    geometry = data["features"][0]["geometry"]
    longitude = geometry["coordinates"][0]
    latitude = geometry["coordinates"][1]

    return longitude, latitude


def import_offres_for_travelling_cinema(user_email: str, filename: str, path: str = DEFAULT_PATH) -> None:
    if path is None and path != DEFAULT_PATH and path.endswith("/"):
        path += "/"

    user = users_models.User.query.filter_by(email=user_email).one()
    non_existent_offerers = set()

    with open(f"{path}{filename}", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.reader(csv_file, delimiter=",")
        for row in csv_rows:
            if _is_header_or_blank_row(row):
                continue
            offer_infos = get_infos_from_data_row(row=row)
            offerer = offerers_models.Offerer.query.filter(
                offerers_models.Offerer.siren == offer_infos["siren"]
            ).one_or_none()
            if not offerer:
                print(f"Offerer with siren={offer_infos['siren']} does not exist")
                non_existent_offerers.add(offer_infos["siren"])
                continue

            venue = check_if_venue_exist_or_create_one(offer_infos, offerer)
            offer = create_offer(offer_infos, venue, user)
            if offer_infos["offer_thumbnail_url"]:
                create_thumbnail(offer, offer_infos["offer_thumbnail_url"], user)
            create_stock(offer_infos, offer, user)

    if non_existent_offerers:
        print(f"{len(non_existent_offerers)} non existent offerer : {non_existent_offerers}")


def check_if_venue_exist_or_create_one(infos: dict, offerer: offerers_models.Offerer) -> offerers_models.Venue:
    venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.managingOffererId == offerer.id)
        .filter(func.lower(offerers_models.Venue.name) == func.lower(infos["venue_name"]))
        .one_or_none()
    )
    longitude, latitude = get_longitude_and_latitude_from_address(
        infos["venue_street"], infos["venue_zip_code"], infos["venue_city"]
    )
    if not venue:
        print(f"Venue with name={infos['venue_name']} does not exist, will be created")
        contact_data = {
            "email": infos["venue_email"],
            "website": infos["venue_website"],
        }
        data = {
            "address": infos["venue_street"],
            "city": infos["venue_city"],
            "postalCode": infos["venue_zip_code"],
            "latitude": latitude,
            "longitude": longitude,
            "managingOffererId": humanize(offerer.id),
            "name": infos["venue_name"],
            "venueTypeCode": "TRAVELING_CINEMA",
            "bookingEmail": infos["venue_email"],
            "comment": infos["comment"],
            "audioDisabilityCompliant": infos["audio_disability_compliant"],
            "mentalDisabilityCompliant": infos["mental_disability_compliant"],
            "motorDisabilityCompliant": infos["motor_disability_compliant"],
            "visualDisabilityCompliant": infos["visual_disability_compliant"],
            "contact": contact_data,
        }
        venue = offerers_api.create_venue(venues_serialize.PostVenueBodyModel(**data))
    return venue


def create_offer(infos: dict, venue: offerers_models.Venue, user: users_models.User) -> offers_models.Offer:

    data = {
        "venueId": humanize(venue.id),
        "subcategoryId": subcategories.CINE_PLEIN_AIR.id,
        "name": infos["offer_name"],
        "description": infos["offer_description"],
        "withdrawalDetails": infos["withdrawal_details"],
        "isDuo": infos["is_duo"],
        "audioDisabilityCompliant": infos["audio_disability_compliant"],
        "mentalDisabilityCompliant": infos["mental_disability_compliant"],
        "motorDisabilityCompliant": infos["motor_disability_compliant"],
        "visualDisabilityCompliant": infos["visual_disability_compliant"],
        "durationMinutes": infos["duration"],
    }
    offer = offers_api.create_offer(offers_serialize.PostOfferBodyModel(**data), user)
    return offer


def create_thumbnail(offer: offers_models.Offer, image_url: str, user: users_models.User) -> None:
    try:
        api_response = requests.get(image_url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as exc:
        logger.exception("Failed to get image from url", extra={"image_url": image_url})
        raise ApiEntrepriseException("Error getting image from url : {}".format(image_url)) from exc

    if api_response.status_code != 200:
        raise ApiEntrepriseException("Error getting image from url : {}".format(image_url))

    offers_api.create_mediation(user=user, offer=offer, credit="", image_as_bytes=api_response.content, keep_ratio=True)


def create_stock(infos: dict, offer: offers_models.Offer, user: users_models.User) -> offers_models.Stock:
    venue = offer.venue
    local_beginning_datetime = datetime.datetime.strptime(
        f"{infos['show_date']} {infos['show_time']}", "%d/%m/%Y %H:%M"
    )
    local_tz = get_department_timezone(venue.departementCode)
    date_in_utc = local_datetime_to_default_timezone(local_beginning_datetime, local_tz)
    quantity = int(infos["quantity"]) if infos["quantity"] else None
    stock_data = {
        "beginningDatetime": date_in_utc,
        "price": float(infos["price"]),
        "quantity": quantity,
        "bookingLimitDatetime": date_in_utc,
    }

    return offers_api.upsert_stocks(offer.id, [stock_serialize.StockCreationBodyModel(**stock_data)], user)[0]


def duration_str_to_minutes(duration: str) -> Optional[int]:
    if not duration:
        return None
    split_duration = duration.split(":")
    hours, minutes = float(split_duration[0]), float(split_duration[1])
    return int(datetime.timedelta(hours=hours, minutes=minutes).total_seconds()) // 60


def get_infos_from_data_row(row: list[str]) -> dict:
    infos = {
        "siren": row[0],
        "venue_email": row[1],
        "venue_type": row[2],
        "comment": row[3],
        "venue_name": row[4],
        "venue_street": row[5],
        "venue_zip_code": row[6],
        "venue_city": row[7],
        "latitude": row[8],
        "longitude": row[9],
        "visual_disability_compliant": row[10].lower() == "oui",
        "mental_disability_compliant": row[11].lower() == "oui",
        "motor_disability_compliant": row[12].lower() == "oui",
        "audio_disability_compliant": row[13].lower() == "oui",
        "not_accessible": row[14].lower() == "oui",
        "venue_website": row[15],
        "offer_category": row[16],
        "offer_subcategory": row[17],
        "offer_name": row[18],
        "offer_description": row[19],
        "offer_thumbnail_url": row[20],
        "duration": duration_str_to_minutes(row[21]),
        "withdrawal_details": row[22],
        "is_duo": row[23].lower() == "oui",
        "show_date": row[24],
        "show_time": row[25],
        "price": row[26],
        "siret": row[27],
        "quantity": row[28],
    }
    return infos
