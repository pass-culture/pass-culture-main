import logging
from dataclasses import dataclass
from typing import Any
from typing import Dict

from pcapi import settings
from pcapi.core.bookings.models import Booking
from pcapi.core.users.models import User
from pcapi.utils import requests


APPS_FLYER_API_URL = "https://api2.appsflyer.com/inappevent"


logger = logging.getLogger(__name__)


@dataclass
class AppsFlyerContext:
    apps_flyer_user_id: str
    platform: str

    def get_app_id(self) -> str:
        if self.platform == "ANDROID":
            return settings.APPS_FLYER_ANDROID_ID
        if self.platform == "IOS":
            return settings.APPS_FLYER_IOS_ID
        return ""

    def get_api_key(self) -> str:
        return settings.APPS_FLYER_API_KEY


class AppsFlyerMissingError(Exception):
    pass


def _send_apps_flyer_event(user: User, event_name: str, event_value: Dict[str, Any], error_context: str) -> None:
    if "apps_flyer" not in user.externalIds:
        raise AppsFlyerMissingError("user has no apps flyer information")

    user_apps_flyer = user.externalIds["apps_flyer"]
    context = AppsFlyerContext(apps_flyer_user_id=user_apps_flyer["user"], platform=user_apps_flyer["platform"])

    base = APPS_FLYER_API_URL.strip("/")
    resource = context.get_app_id().strip("/")
    url = f"{base}/{resource}"

    headers = {"authentication": context.get_api_key(), "Content-Type": "application/json"}
    data = {
        "appsflyer_id": context.apps_flyer_user_id,
        "eventName": event_name,
        "eventValue": event_value,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
    except (ConnectionError, requests.exceptions.RequestException) as error:
        extra_infos = {
            "user": user.id,
            "user.apps_flyer_id": context.apps_flyer_user_id,
            "event_name": event_name,
            "error": str(error),
        }
        logger.error("[APPS FLYER][%s] request failed", error_context, extra=extra_infos)
        return

    if response.status_code != 200:
        extra_infos = {
            "user": user.id,
            "user.apps_flyer_id": context.apps_flyer_user_id,
            "event_name": event_name,
            "code": response.status_code,
            "text": response.text,
        }
        logger.error("[APPS FLYER][%s] request returned an error", error_context, extra=extra_infos)


def log_user_event(user: User, event_name: str) -> None:
    user_firebase_pseudo_id = user.externalIds.get("firebase_pseudo_id", "")
    event_value = {
        "af_user_id": str(user.id),
        "af_firebase_pseudo_id": user_firebase_pseudo_id,
        "type": user.deposit.type.value if user.deposit else None,
    }
    _send_apps_flyer_event(user, event_name, event_value, "BECOMES BENEFICIARY")


def log_offer_event(booking: Booking, event_name: str) -> None:
    event_value = {
        "af_user_id": str(booking.userId),
        "af_offer_id": str(booking.stock.offerId),
        "af_booking_id": str(booking.id),
        "af_price": str(booking.amount),
        "af_category": booking.stock.offer.subcategoryId,
    }
    _send_apps_flyer_event(booking.user, event_name, event_value, "OFFER BOOKED")
