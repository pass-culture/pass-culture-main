from typing import Optional
from urllib.parse import urlencode

from pcapi import settings
from pcapi.models.feature import FeatureToggle


def get_webapp_for_native_redirection_url() -> Optional[str]:
    if FeatureToggle.WEBAPP_V2_ENABLED.is_active():
        return settings.WEBAPP_V2_URL
    return settings.WEBAPP_FOR_NATIVE_REDIRECTION


def get_webapp_url() -> Optional[str]:
    if FeatureToggle.WEBAPP_V2_ENABLED.is_active():
        return settings.WEBAPP_V2_URL
    return settings.WEBAPP_URL


def generate_firebase_dynamic_link(path: str, params: Optional[dict]) -> str:
    universal_link_url = f"{get_webapp_for_native_redirection_url()}/{path}"
    if params:
        universal_link_url = universal_link_url + f"?{urlencode(params)}"

    firebase_dynamic_query_string = urlencode({"link": universal_link_url})
    return f"{settings.FIREBASE_DYNAMIC_LINKS_URL}/?{firebase_dynamic_query_string}"
