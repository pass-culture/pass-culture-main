import csv
import datetime
import logging

from sqlalchemy import func

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


# main script
def import_offers_for_travelling_cinema(user_email: str, filename: str, path: str = DEFAULT_PATH) -> None:
    if path is None and path != DEFAULT_PATH and path.endswith("/"):
        path += "/"

    user = users_models.User.query.filter_by(email=user_email).one()
    non_existent_offerers = set()
    row_number_list_error_to_complete_address = []
    row_number_list_error_to_create_venue = []
    row_number_list_error_to_create_offer = []
    row_number_list_error_to_create_thumbnail = []
    row_number_list_error_to_create_stock = []

    with open(f"{path}{filename}", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.reader(csv_file, delimiter=",")
        for row_number, row in enumerate(csv_rows):
            if _is_header_or_blank_row(row):
                continue
            infos = _get_infos_from_data_row(row=row)
            offerer = offerers_models.Offerer.query.filter(
                offerers_models.Offerer.siren == infos["siren"]
            ).one_or_none()
            if not offerer:
                non_existent_offerers.add(infos["siren"])
                continue

            venue = _get_venue(infos, offerer)

            if not venue:
                try:
                    infos = _complete_address_and_coordinates_data(infos)
                    is_address_completed = (
                        infos["venue_street"]
                        and infos["venue_zip_code"]
                        and infos["venue_city"]
                        and infos["longitude"]
                        and infos["latitude"]
                    )
                except Exception:  # pylint: disable=broad-except
                    row_number_list_error_to_complete_address.append(row_number)

                if is_address_completed:
                    try:
                        venue = _create_venue(infos, offerer)
                    except Exception:  # pylint: disable=broad-except
                        row_number_list_error_to_create_venue.append(row_number)

            if venue:
                try:
                    offer = _create_offer(infos, venue, user)
                except Exception:  # pylint: disable=broad-except
                    row_number_list_error_to_create_offer.append(row_number)
                if infos["offer_thumbnail_url"]:
                    try:
                        _create_thumbnail(offer, infos["offer_thumbnail_url"], user)
                    except Exception:  # pylint: disable=broad-except
                        row_number_list_error_to_create_thumbnail.append(row_number)
                try:
                    _create_stock(infos, offer, user)
                except Exception:  # pylint: disable=broad-except
                    row_number_list_error_to_create_stock.append(row_number)

    if non_existent_offerers:
        print(f"{len(non_existent_offerers)} non existent offerer : {non_existent_offerers}")

    if row_number_list_error_to_complete_address:
        print(
            f"{len(row_number_list_error_to_complete_address)} error(s) to complete address at row number :"
            f"{row_number_list_error_to_complete_address}"
        )

    if row_number_list_error_to_create_venue:
        print(
            f"{len(row_number_list_error_to_create_venue)} error(s) to create venue at row number :"
            f"{row_number_list_error_to_create_venue}"
        )

    if row_number_list_error_to_create_offer:
        print(
            f"{len(row_number_list_error_to_create_offer)} error(s) to create offer at row number :"
            f"{row_number_list_error_to_create_offer}"
        )

    if row_number_list_error_to_create_thumbnail:
        print(
            f"{len(row_number_list_error_to_create_thumbnail)} error(s) to create thumbnail at row number :"
            f"{row_number_list_error_to_create_thumbnail}"
        )

    if row_number_list_error_to_create_stock:
        print(
            f"{len(row_number_list_error_to_create_stock)} error(s) to create stock at row number :"
            f"{row_number_list_error_to_create_stock}"
        )


def _get_infos_from_data_row(row: list[str]) -> dict:
    infos = {
        "siren": row[0],
        "venue_email": row[1],
        "venue_type": row[2],
        "comment": row[3],
        "venue_name": row[4],
        "venue_street": row[5],
        "venue_zip_code": clean_venue_zip_code(row[6]),
        "venue_city": row[7],
        "latitude": replace_comma_by_dot(row[8]),
        "longitude": replace_comma_by_dot(row[9]),
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
        "duration": _duration_str_to_minutes(row[21]),
        "withdrawal_details": row[22],
        "is_duo": row[23].lower() == "oui",
        "show_date": row[24],
        "show_time": row[25],
        "price": row[26],
        "siret": row[27],
        "quantity": row[28],
    }
    return infos


def replace_comma_by_dot(string: str) -> str:
    return string.replace(",", ".")


def clean_venue_zip_code(zip_code: str) -> str:
    if len(zip_code) == 4:
        zip_code = "0" + zip_code
    return zip_code


def _is_header_or_blank_row(row: list[str]) -> bool:
    return not row or not row[0] or row[0] == "Identifiant du compte (SIREN)"


def _get_venue(infos: dict, offerer: offerers_models.Offerer) -> offerers_models.Venue | None:
    return (
        offerers_models.Venue.query.filter(offerers_models.Venue.managingOffererId == offerer.id)
        .filter(func.lower(offerers_models.Venue.name) == func.lower(infos["venue_name"]))
        .one_or_none()
    )


def _create_venue(infos: dict, offerer: offerers_models.Offerer) -> offerers_models.Venue:
    contact_data = {
        "email": infos["venue_email"],
        "website": infos["venue_website"],
    }
    data = {
        "address": infos["venue_street"],
        "postalCode": infos["venue_zip_code"],
        "city": infos["venue_city"],
        "longitude": infos["longitude"],
        "latitude": infos["latitude"],
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


def _complete_address_and_coordinates_data(infos: dict) -> dict:
    siren = infos["siren"]
    street = infos["venue_street"]
    zip_code = infos["venue_zip_code"]
    city = infos["venue_city"]
    longitude = infos["longitude"]
    latitude = infos["latitude"]
    if street and zip_code and city:
        longitude, latitude = _get_longitude_and_latitude_from_address(street, zip_code, city)
    else:
        if longitude and latitude:
            street, zip_code, city = _get_address_from_longitude_and_latitude(longitude=longitude, latitude=latitude)

    infos["siren"] = siren
    infos["venue_street"] = street
    infos["venue_zip_code"] = zip_code
    infos["venue_city"] = city
    infos["longitude"] = longitude
    infos["latitude"] = latitude
    return infos


def _get_longitude_and_latitude_from_address(street: str, zip_code: str, city: str) -> tuple[float, float]:
    address = f"{street} {zip_code} {city}"

    url = f"https://api-adresse.data.gouv.fr/search/?limit=1&q={address}"
    try:
        response = requests.get(url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as exc:
        logger.exception("Failed to get data from api-adresse.data.gouv.fr", extra={"address": address})
        raise Exception("ERR : Error getting API adresse for address : {}".format(address)) from exc

    if response.status_code != 200:
        raise Exception("ERR : Error getting API adresse for adress : {}".format(address))

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
        raise Exception("ERR : Error getting API adresse for lon, lat : {} {}".format(longitude, latitude)) from exc

    if response.status_code != 200:
        raise Exception("ERR : Error getting API adresse for lon, lat : {} {}".format(longitude, latitude))

    data = response.json()
    properties = data["features"][0]["properties"]
    street = properties["name"]
    zip_code = properties["postcode"]
    city = properties["city"]

    return street, zip_code, city


def _create_offer(infos: dict, venue: offerers_models.Venue, user: users_models.User) -> offers_models.Offer:
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


def _create_thumbnail(offer: offers_models.Offer, image_url: str, user: users_models.User) -> None:
    try:
        api_response = requests.get(image_url)
        offers_api.create_mediation(
            user=user, offer=offer, credit="", image_as_bytes=api_response.content, keep_ratio=True
        )
    except Exception:  # pylint: disable=broad-except
        pass


def _create_stock(infos: dict, offer: offers_models.Offer, user: users_models.User) -> offers_models.Stock:
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


def _duration_str_to_minutes(duration: str) -> int | None:
    if not duration:
        return None
    hours = 0
    minutes = 0
    split_duration = duration.split(":")
    if len(split_duration) == 1:
        hours = int(split_duration[0])
    elif len(split_duration) > 1:
        hours, minutes = int(split_duration[0]), int(split_duration[1])

    return int(datetime.timedelta(hours=hours, minutes=minutes).total_seconds()) // 60
