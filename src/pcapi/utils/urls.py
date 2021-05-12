from urllib.parse import urlencode

from pcapi import settings


def generate_firebase_dynamic_link(path: str, params: dict) -> str:
    universal_link_query_string = urlencode(params)
    universal_link_url = f"{settings.NATIVE_APP_URL}/{path}?{universal_link_query_string}"
    firebase_dynamic_query_string = urlencode({"link": universal_link_url})
    return f"{settings.FIREBASE_DYNAMIC_LINKS_URL}/?{firebase_dynamic_query_string}"
