from urllib.parse import urlencode

from pcapi import settings
from pcapi.core.bookings.models import Booking


def generate_firebase_dynamic_link(path: str, params: dict | None) -> str:
    universal_link_url = f"{settings.WEBAPP_V2_URL}/{path}"
    if params:
        universal_link_url = universal_link_url + f"?{urlencode(params)}"

    firebase_dynamic_query_string = urlencode({"link": universal_link_url})
    return f"{settings.FIREBASE_DYNAMIC_LINKS_URL}/?{firebase_dynamic_query_string}"


def booking_app_link(booking: Booking) -> str:
    return f"{settings.WEBAPP_V2_URL}/reservation/{booking.id}/details"
