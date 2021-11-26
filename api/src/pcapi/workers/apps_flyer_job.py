from dataclasses import dataclass
import logging

from requests.exceptions import RequestException

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
        if self.platform == "ANDROID":
            return settings.APPS_FLYER_ANDROID_API_KEY
        if self.platform == "IOS":
            return settings.APPS_FLYER_IOS_API_KEY
        return ""


class AppsFlyerMissingError(Exception):
    pass


@job(worker.default_queue)
def log_user_becomes_beneficiary_event_job(user_id: int) -> None:
    user = User.query.get(user_id)

    if "apps_flyer" not in user.externalIds:
        raise AppsFlyerMissingError("user has no apps flyer information")

    user_apps_flyer = user.externalIds["apps_flyer"]
    context = AppsFlyerContext(apps_flyer_user_id=user_apps_flyer["user"], platform=user_apps_flyer["platform"])

    base = APPS_FLYER_API_URL.strip("/")
    resource = context.get_app_id().strip("/")
    url = f"{base}/{resource}"

    headers = {"authentication": context.get_api_key(), "Content-Type": "application/json"}
    data = {
        "customer_user_id": str(user.id),
        "appsflyer_id": context.apps_flyer_user_id,
        "eventName": "af_complete_beneficiary_registration",
        "eventValue": {"af_user_id": str(user.id)},
    }

    try:
        response = requests.post(url, headers=headers, json=data)
    except (ConnectionError, RequestException) as error:
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
