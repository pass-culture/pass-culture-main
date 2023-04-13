import datetime
import enum
import json
import logging
import urllib.parse

import requests

from pcapi import settings
from pcapi.core.offerers import models as offerers_models
from pcapi.utils.regions import get_region_name_from_department


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
    def create_offerer(self, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        raise NotImplementedError()

    def update_offerer(self, zendesk_id: int, offerer: offerers_models.Offerer) -> dict:
        raise NotImplementedError()

    def create_venue(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        raise NotImplementedError()

    def update_venue(self, zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
        raise NotImplementedError()

    def search_contact(self, params: dict, session: requests.Session | None = None) -> dict:
        body = self._query_api("POST", "/v3/contacts/search", body=params, session=session)

        # Response format:
        # https://developer.zendesk.com/api-reference/sales-crm/search/response/

        item_dict = list(body.values())[0][0]
        total_count: int = item_dict["meta"]["total_count"]  # how many results for the query string

        if total_count == 1:
            return item_dict["items"][0]["data"]
        if total_count > 1:
            raise ContactFoundMoreThanOneError([item["data"] for item in item_dict["items"]])
        raise ContactNotFoundError

    def _query_api(self, method: str, path: str, body: str | dict | None, session: requests.Session | None) -> dict:
        if not session:
            session = self._configure_session()

        match method.upper():
            case "PUT":
                response = session.put(self._build_url(path), json=body)
            case "POST":
                response = session.post(self._build_url(path), json=body)
            case "GET":
                response = session.get(self._build_url(path))
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

    def _get_venue_data(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = False
    ) -> dict:
        # Call once to avoid two db calls
        has_collective_offers = venue.has_collective_offers

        if venue.has_individual_offers or has_collective_offers:
            if venue.has_approved_offers:
                pc_pro_status = "Acteur Inscrit Actif"
            else:
                pc_pro_status = "Acteur Inscrit non Actif"
        else:
            pc_pro_status = "Acteur en cours d'inscription"

        social_medias = getattr(venue.contact, "social_medias", {})
        params: dict = {
            "data": {
                "is_organization": True,
                # "name" is not updated because sometimes the name in the product is not the same in Zendesk Sell,
                "parent_organization_id": parent_organization_id,  # if None, then it will send null on the request
                "last_name": "",  # leave that empty for the Zendesk api
                "description": venue.description,
                "industry": venue.venueTypeCode.value,
                "website": venue.contact.website if venue.contact else None,
                "email": venue.bookingEmail,
                "phone": venue.contact.phone_number if venue.contact else None,
                "twitter": social_medias.get("twitter", ""),
                "facebook": social_medias.get("facebook", ""),
                "address": {
                    "line1": venue.address,
                    "city": venue.city,
                    "postal_code": venue.postalCode,
                },
                "custom_fields": {
                    ZendeskCustomFieldsNames.DEPARTEMENT.value: venue.departementCode,
                    ZendeskCustomFieldsNames.INTERNAL_COMMENT.value: "Mis à jour par le produit le %s"
                    % (datetime.date.today().strftime("%d/%m/%Y")),
                    ZendeskCustomFieldsNames.HAS_PUBLISHED_COLLECTIVE_OFFERS.value: has_collective_offers,
                    ZendeskCustomFieldsNames.JURIDIC_NAME.value: venue.name,
                    ZendeskCustomFieldsNames.PC_PRO_STATUS.value: pc_pro_status,
                    ZendeskCustomFieldsNames.PRODUCT_VENUE_ID.value: venue.id,
                    ZendeskCustomFieldsNames.SIRET.value: venue.siret,
                    ZendeskCustomFieldsNames.REGION.value: get_region_name_from_department(
                        venue.departementCode
                    ).upper(),
                    ZendeskCustomFieldsNames.TYPAGE.value: ["Lieu"],
                    ZendeskCustomFieldsNames.BACKOFFICE_LINK.value: self._build_backoffice_venue_link(venue),
                    ZendeskCustomFieldsNames.UPDATED_IN_PRODUCT.value: datetime.datetime.utcnow().isoformat(),
                },
            }
        }

        if created:
            params["data"]["custom_fields"][ZendeskCustomFieldsNames.CREATED_FROM_PRODUCT.value] = True

        return params

    def _get_offerer_data(self, offerer: offerers_models.Offerer, created: bool = False) -> dict:
        params: dict = {
            "data": {
                "is_organization": True,
                # "name" is not updated because sometimes the name in the product is not the same in Zendesk Sell,
                "last_name": "",
                "address": {
                    "line1": offerer.address,
                    "city": offerer.city,
                    "postal_code": offerer.postalCode,
                },
                "custom_fields": {
                    ZendeskCustomFieldsNames.DEPARTEMENT.value: offerer.departementCode,
                    ZendeskCustomFieldsNames.INTERNAL_COMMENT.value: "Mis à jour par le produit le %s"
                    % (datetime.date.today().strftime("%d/%m/%Y"),),
                    ZendeskCustomFieldsNames.JURIDIC_NAME.value: offerer.name,
                    ZendeskCustomFieldsNames.PRODUCT_OFFERER_ID.value: offerer.id,
                    ZendeskCustomFieldsNames.REGION.value: get_region_name_from_department(offerer.departementCode).upper(),  # type: ignore [arg-type]
                    ZendeskCustomFieldsNames.SIREN.value: offerer.siren,
                    ZendeskCustomFieldsNames.TYPAGE.value: ["Structure"],
                    ZendeskCustomFieldsNames.BACKOFFICE_LINK.value: self._build_backoffice_offerer_link(offerer),
                    ZendeskCustomFieldsNames.UPDATED_IN_PRODUCT.value: datetime.datetime.utcnow().isoformat(),
                },
            }
        }

        if created:
            params["data"]["custom_fields"][ZendeskCustomFieldsNames.CREATED_FROM_PRODUCT.value] = True

        return params
