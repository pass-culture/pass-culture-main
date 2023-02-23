from dataclasses import dataclass
import logging

from pcapi import settings


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
