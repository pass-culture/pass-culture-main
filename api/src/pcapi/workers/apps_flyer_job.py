from dataclasses import dataclass
import logging

from pcapi import settings
from pcapi.core.users.models import User
from pcapi.utils import requests
from pcapi.workers import worker
from pcapi.workers.decorators import job


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


@job(worker.default_queue)
def log_user_becomes_beneficiary_event_job(user_id: int) -> None:
    user = User.query.filter_by(id=user_id).one()

    if "apps_flyer" not in user.externalIds:
        raise AppsFlyerMissingError("user has no apps flyer information")

    user_apps_flyer = user.externalIds["apps_flyer"]
    user_firebase_pseudo_id = user.externalIds.get("firebase_pseudo_id", "")
    context = AppsFlyerContext(apps_flyer_user_id=user_apps_flyer["user"], platform=user_apps_flyer["platform"])

    base = APPS_FLYER_API_URL.strip("/")
    resource = context.get_app_id().strip("/")
    url = f"{base}/{resource}"

    headers = {"authentication": context.get_api_key(), "Content-Type": "application/json"}
    data = {
        "appsflyer_id": context.apps_flyer_user_id,
        "eventName": "af_complete_beneficiary",
        "eventValue": {
            "af_user_id": str(user.id),
            "af_firebase_pseudo_id": user_firebase_pseudo_id,
            "type": user.deposit.type.value,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=data)
    except (ConnectionError, requests.exceptions.RequestException) as error:
        extra_infos = {"user": user.id, "user.apps_flyer_id": context.apps_flyer_user_id, "error": str(error)}
        logger.error("[APPS FLYER][BECOMES BENEFICIARY] request failed", extra=extra_infos)
        return

    if response.status_code != 200:
        extra_infos = {
            "user": user.id,
            "user.apps_flyer_id": context.apps_flyer_user_id,
            "code": response.status_code,
            "text": response.text,
        }
        logger.error("[APPS FLYER][BECOMES BENEFICIARY] request returned an error", extra=extra_infos)
