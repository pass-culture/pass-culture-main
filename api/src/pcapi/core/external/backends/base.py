import enum
import json
import logging
import urllib.parse

import requests

from pcapi import settings
from pcapi.core.offerers import models as offerers_models


logger = logging.getLogger(__name__)

ZENDESK_SELL_API_KEY = settings.ZENDESK_SELL_API_KEY
ZENDESK_SELL_API_URL = settings.ZENDESK_SELL_API_URL
BACKOFFICE_URL = settings.BACKOFFICE_URL

SEARCH_PARENT = -1


class ZendeskError(Exception):
    """Base class for Zendesk exceptions"""


class ContactFoundMoreThanOneError(ZendeskError):
    """Raised when the search returns more than one result"""

    def __init__(self, items: list):
        super().__init__()
        self.items = items


class ContactNotFoundError(ZendeskError):
    """Raised when the search returns no result"""


class ZendeskCustomFieldsShort(enum.Enum):
    CREATED_FROM_PRODUCT = "contact:4454978"
    DEPARTEMENT = "contact:4325526"
    FIRST_PUBLISHED_OFFER = "contact:4307495"
    HAS_PUBLISHED_COLLECTIVE_OFFERS = "contact:4307491"
    INTERNAL_COMMENT = "contact:4586448"
    JURIDIC_NAME = "contact:4307445"
    PC_PRO_STATUS = "contact:4307489"
    PRODUCT_OFFERER_ID = "contact:4308851"
    PRODUCT_VENUE_ID = "contact:4308850"
    REGION = "contact:4307444"
    SIREN = "contact:4308852"
    SIRET = "contact:4308853"
    TYPAGE = "contact:4308855"
    UPDATE_IN_PRODUCT = "contact:4454825"
    BACKOFFICE_LINK = "contact:4308856"


class ZendeskCustomFieldsNames(enum.Enum):
    CREATED_FROM_PRODUCT = "Créé depuis produit"
    UPDATED_IN_PRODUCT = "Date de mise à jour produit"
    DEPARTEMENT = "Département"
    FIRST_PUBLISHED_OFFER = "Première offre publiée"
    HAS_PUBLISHED_COLLECTIVE_OFFERS = "A publié une offre EAC collectif"
    INTERNAL_COMMENT = "Commentaire interne#1"
    JURIDIC_NAME = "Nom juridique"
    PC_PRO_STATUS = "Statut PC Pro"
    PRODUCT_OFFERER_ID = "Produit Offerer ID"
    PRODUCT_VENUE_ID = "Produit Venue ID"
    REGION = "Région"
    SIREN = "SIREN"
    SIRET = "SIRET"
    TYPAGE = "Typage"
    BACKOFFICE_LINK = "Lien vers page BO"


class BaseBackend:
    def __init__(self) -> None:
        self.session = self._configure_session()

    def create_offerer(self, offerer: offerers_models.Offerer, created: bool = False) -> dict:
        raise NotImplementedError()

    def update_offerer(self, zendesk_id: int, offerer: offerers_models.Offerer) -> dict:
        raise NotImplementedError()

    def create_venue(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = False
    ) -> dict:
        raise NotImplementedError()

    def update_venue(self, zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
        raise NotImplementedError()

    def search_contact(self, params: dict) -> dict:
        raise NotImplementedError()

    def get_offerer_by_id(self, offerer: offerers_models.Offerer) -> dict:
        raise NotImplementedError()

    def get_venue_by_id(self, venue: offerers_models.Venue) -> dict:
        raise NotImplementedError()

    def query_api(self, method: str, path: str, body: str | dict | None) -> dict:
        if not self.session:
            self._configure_session()

        match method.upper():
            case "PUT":
                response = self.session.put(self._build_url(path), json=body)
            case "POST":
                response = self.session.post(self._build_url(path), json=body)
            case "GET":
                response = self.session.get(self._build_url(path))
            case _:
                raise ValueError("Unsupported method")
        if not response.ok:
            logger.error(
                "Error %s while calling Zendesk Sell API",
                response.status_code,
                extra={
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "response": response.content,
                    "body": json.dumps(body, indent=4),
                },
            )
        response.raise_for_status()
        # All APIs called here return json content
        return response.json()

    def _configure_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": "Bearer " + ZENDESK_SELL_API_KEY,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        return session

    def _build_url(self, path: str) -> str:
        return urllib.parse.urljoin(ZENDESK_SELL_API_URL, path)

    def _build_backoffice_offerer_link(self, offerer: offerers_models.Offerer) -> str:
        return urllib.parse.urljoin(BACKOFFICE_URL, f"pro/offerer/{offerer.id}")

    def _build_backoffice_venue_link(self, venue: offerers_models.Venue) -> str:
        return urllib.parse.urljoin(BACKOFFICE_URL, f"pro/venue/{venue.id}")
