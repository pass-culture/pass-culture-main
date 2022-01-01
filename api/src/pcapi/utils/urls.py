from typing import Optional
from urllib.parse import urlencode

from pcapi import settings


def generate_firebase_dynamic_link(path: str, params: Optional[dict]) -> str:
    universal_link_url = f"{settings.WEBAPP_V2_URL}/{path}"
    if params:
        universal_link_url = universal_link_url + f"?{urlencode(params)}"

    firebase_dynamic_query_string = urlencode({"link": universal_link_url})
    return f"{settings.FIREBASE_DYNAMIC_LINKS_URL}/?{firebase_dynamic_query_string}"
