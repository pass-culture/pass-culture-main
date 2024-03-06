"""
A client for API Acceslibre.
Documentation of the API: https://acceslibre.beta.gouv.fr/api/docs/
Further explanations at: https://schema.data.gouv.fr/MTES-MCT/acceslibre-schema/0.0.14/documentation.html
"""

import json
import logging

from rapidfuzz import fuzz

from pcapi import settings
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)

ACCESLIBRE_REQUEST_TIMEOUT = 3
REQUEST_PAGE_SIZE = 50
MATCHING_RATIO = 50


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.ACCESLIBRE_BACKEND)
    return backend_class()


def find_venue_at_accessibility_provider(
    name: str,
    public_name: str | None = None,
    siret: str | None = None,
    ban_id: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
) -> str | None:
    """Try to find the entry at acceslibre that matches our venue
    Returns acceslibre slug (which is unique and safe according to them)
    """
    return _get_backend().find_venue_at_accessibility_provider(
        name=name,
        public_name=public_name,
        siret=siret,
        ban_id=ban_id,
        city=city,
        postal_code=postal_code,
    )


def match_by_name(results_at_provider: list[dict[str, str]], name: str, public_name: str | None) -> str | None:
    name = name.lower()
    public_name = public_name.lower() if public_name else "PUBLIC_NAME_MISSING"
    for erp in results_at_provider:
        name_at_provider = erp["nom"].lower()
        if (
            name_at_provider in name
            or name in name_at_provider
            or public_name in name_at_provider
            or name_at_provider in public_name
        ):
            return erp["slug"]
        if (
            fuzz.ratio(name_at_provider, name) > MATCHING_RATIO
            or fuzz.ratio(name_at_provider, public_name) > MATCHING_RATIO
        ):
            return erp["slug"]
    return None


class AccesLibreApiException(Exception):
    pass


class BaseBackend:
    def find_venue_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
    ) -> str | None:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def find_venue_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
    ) -> str | None:
        return "mon-lieu-chez-acceslibre"


class AcceslibreBackend(BaseBackend):
    def _send_request(
        self,
        query_params: dict[str, str],
    ) -> dict:
        api_key = settings.ACCESLIBRE_API_KEY
        url = settings.ACCESLIBRE_API_URL
        headers = {"Authorization": f"Api-Key {api_key}"}
        try:
            response = requests.get(url, headers=headers, params=query_params, timeout=ACCESLIBRE_REQUEST_TIMEOUT)
        except requests.exceptions.RequestException:
            raise AccesLibreApiException(
                f"Error connecting AccesLibre API for {url} and query parameters: {query_params}"
            )
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.error(
                "Got non-JSON or malformed JSON response from AccesLibre",
                extra={"url": response.url, "response": response.content},
            )
            raise AccesLibreApiException(f"Non-JSON response from AccesLibre API for {response.url}")

    def find_venue_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
    ) -> str | None:
        search_criteria: list[dict] = [
            {"siret": siret},
            {"ban_id": ban_id},
            {
                "q": name,
                "commune": city,
                "code_postal": postal_code,
                "page_size": REQUEST_PAGE_SIZE,
            },
            {
                "q": public_name,
                "commune": city,
                "code_postal": postal_code,
                "page_size": REQUEST_PAGE_SIZE,
            },
        ]

        for criterion in search_criteria:
            if all(v is not None for v in criterion.values()):
                response = self._send_request(query_params=criterion)
                if response["count"] and (
                    slug := match_by_name(results_at_provider=response["results"], name=name, public_name=public_name)
                ):
                    return slug
        return None
