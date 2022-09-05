import datetime
import enum
import json
import logging
import urllib.parse

import requests

from pcapi import settings
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.users import testing
from pcapi.models.feature import FeatureToggle
from pcapi.tasks import zendesk_sell_tasks


logger = logging.getLogger(__name__)

ZENDESK_SELL_API_KEY = settings.ZENDESK_SELL_API_KEY
ZENDESK_SELL_API_URL = settings.ZENDESK_SELL_API_URL
BACKOFFICE_URL = settings.BACKOFFICE_URL

SEARCH_PARENT = -1

REGIONS = {
    "Auvergne-Rhone-Alpes": ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"],
    "Bourgogne-Franche-Comte": ["21", "25", "39", "58", "70", "71", "89", "90"],
    "Bretagne": ["35", "22", "56", "29"],
    "Centre-Val de Loire": ["18", "28", "36", "37", "41", "45"],
    "Corse": ["2A", "2B", "20"],
    "Grand Est": ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"],
    "Guadeloupe": ["971"],
    "Guyane": ["973"],
    "Hauts-de-France": ["02", "59", "60", "62", "80"],
    "Ile-de-France": ["75", "77", "78", "91", "92", "93", "94", "95"],
    "La Reunion": ["974"],
    "Martinique": ["972"],
    "Mayotte": ["976"],
    "Normandie": ["14", "27", "50", "61", "76"],
    "Nouvelle-Aquitaine": ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"],
    "Occitanie": ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"],
    "Pays de la Loire": ["44", "49", "53", "72", "85"],
    "Provence-Alpes-Cote d'Azur": ["04", "05", "06", "13", "83", "84"],
}


def _get_region_name_from_departement(departement: str | None) -> str:
    if departement:
        for region, departements in REGIONS.items():
            if departement in departements:
                return region.upper()
    return "Aucune valeur"


def _build_backoffice_offerer_link(offerer: offerers_models.Offerer) -> str:
    return urllib.parse.urljoin(BACKOFFICE_URL, f"offerers/{offerer.id}")


def _build_backoffice_venue_link(venue: offerers_models.Venue) -> str:
    return urllib.parse.urljoin(BACKOFFICE_URL, f"venues/{venue.id}")


class ZendeskError(Exception):
    """Base class for Zendesk exceptions"""


class ContactFoundMoreThanOneError(ZendeskError):
    """Raised when the search returns more than one result"""

    def __init__(self, items):  # type: ignore [no-untyped-def]
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


def configure_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": "Bearer " + ZENDESK_SELL_API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )

    return session


def _build_url(path: str) -> str:
    return urllib.parse.urljoin(ZENDESK_SELL_API_URL, path)


def _query_api(method: str, path: str, body: str | dict | None) -> dict:
    session = configure_session()
    match method.upper():
        case "PUT":
            response = session.put(_build_url(path), json=body)
        case "POST":
            response = session.post(_build_url(path), json=body)
        case "GET":
            response = session.get(_build_url(path))
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


def _get_venue_data(venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = False) -> dict:
    social_medias = getattr(venue.contact, "social_medias", {})
    params: dict = {
        "data": {
            "is_organization": True,
            "name": venue.publicName if venue.publicName else venue.name,
            "parent_organization_id": parent_organization_id,  # if None, then it will send null on the request
            "last_name": "",  # leave that empty for the Zendesk api
            "description": venue.description,
            "industry": venue.venueType.label if venue.venueType else None,
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
                ZendeskCustomFieldsNames.HAS_PUBLISHED_COLLECTIVE_OFFERS.value: len(venue.collectiveOffers) > 0,
                ZendeskCustomFieldsNames.JURIDIC_NAME.value: venue.name,
                ZendeskCustomFieldsNames.PC_PRO_STATUS.value: _get_venue_status(venue),
                ZendeskCustomFieldsNames.PRODUCT_VENUE_ID.value: venue.id,
                ZendeskCustomFieldsNames.SIRET.value: venue.siret,
                ZendeskCustomFieldsNames.REGION.value: _get_region_name_from_departement(venue.departementCode),
                ZendeskCustomFieldsNames.TYPAGE.value: ["Lieu"],
                ZendeskCustomFieldsNames.BACKOFFICE_LINK.value: _build_backoffice_venue_link(venue),
                ZendeskCustomFieldsNames.UPDATED_IN_PRODUCT.value: datetime.datetime.utcnow().isoformat(),
            },
        }
    }

    if created:
        params["data"]["custom_fields"][ZendeskCustomFieldsNames.CREATED_FROM_PRODUCT.value] = True

    return params


def _get_offerer_data(offerer: offerers_models.Offerer, created: bool = False) -> dict:
    params: dict = {
        "data": {
            "is_organization": True,
            "name": offerer.name if offerer.name else "N/A",
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
                ZendeskCustomFieldsNames.REGION.value: _get_region_name_from_departement(offerer.departementCode),  # type: ignore [arg-type]
                ZendeskCustomFieldsNames.SIREN.value: offerer.siren,
                ZendeskCustomFieldsNames.TYPAGE.value: ["Structure"],
                ZendeskCustomFieldsNames.BACKOFFICE_LINK.value: _build_backoffice_offerer_link(offerer),
                ZendeskCustomFieldsNames.UPDATED_IN_PRODUCT.value: datetime.datetime.utcnow().isoformat(),
            },
        }
    }

    if created:
        params["data"]["custom_fields"][ZendeskCustomFieldsNames.CREATED_FROM_PRODUCT.value] = True

    return params


def _search_contact(params: dict) -> dict:
    body = _query_api("POST", "/v3/contacts/search", body=params)

    # Response format:
    # https://developer.zendesk.com/api-reference/sales-crm/search/response/

    item_dict = list(body.values())[0][0]
    total_count: int = item_dict["meta"]["total_count"]  # how many results for the query string

    if total_count == 1:
        return item_dict["items"][0]["data"]
    if total_count > 1:
        raise ContactFoundMoreThanOneError([item["data"] for item in item_dict["items"]])
    raise ContactNotFoundError


def is_offerer_only_virtual(offerer: offerers_models.Offerer) -> bool:
    return offerer.managedVenues and all(venue.isVirtual for venue in offerer.managedVenues)


def get_offerer_by_id(offerer: offerers_models.Offerer) -> dict:
    # (offerer id OR siren) AND NO venue id AND NO siret
    offerer_filter: dict = {
        "filter": {
            "attribute": {"name": "custom_fields." + ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value},
            "parameter": {"eq": offerer.id},
        }
    }

    if offerer.siren:
        offerer_filter = {
            "or": [
                offerer_filter,
                {
                    "filter": {
                        "attribute": {"name": "custom_fields." + ZendeskCustomFieldsShort.SIREN.value},
                        "parameter": {"eq": offerer.siren},
                    }
                },
            ]
        }

    params = {
        "items": [
            {
                "data": {
                    "query": {
                        "filter": {
                            "and": [
                                {
                                    "filter": {
                                        "attribute": {"name": "is_organisation"},
                                        "parameter": {"eq": True},
                                    }
                                },
                                offerer_filter,
                                {
                                    "or": [
                                        {
                                            "filter": {
                                                "attribute": {
                                                    "name": "custom_fields."
                                                    + ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value
                                                },
                                                "parameter": {"is_null": True},
                                            }
                                        },
                                        {
                                            "filter": {
                                                "attribute": {
                                                    "name": "custom_fields."
                                                    + ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value
                                                },
                                                "parameter": {"eq": "0"},
                                            }
                                        },
                                    ]
                                },
                                {
                                    "filter": {
                                        "attribute": {"name": "custom_fields." + ZendeskCustomFieldsShort.SIRET.value},
                                        "parameter": {"is_null": True},
                                    }
                                },
                            ]
                        },
                        "projection": [
                            {"name": "id"},
                            {"name": f"custom_fields.{ZendeskCustomFieldsShort.SIREN.value}"},
                            {"name": f"custom_fields.{ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value}"},
                        ],
                    }
                }
            },
        ]
    }

    try:
        return _search_contact(params)
    except ContactFoundMoreThanOneError as e:
        contacts = e.items

        # looking for the item that has a product offerer id amongst the found items
        contacts_with_offerer_id = [
            contact
            for contact in contacts
            if contact["custom_fields"][ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value] == str(offerer.id)
        ]

        # we found just one result, we assume it's the offerer, the others seems to be the venues
        if len(contacts_with_offerer_id) == 1:
            return contacts_with_offerer_id[0]
        raise


def get_venue_by_id(venue: offerers_models.Venue) -> dict:
    venue_filter: dict = {
        "filter": {
            "attribute": {"name": f"custom_fields.{ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value}"},
            "parameter": {"eq": venue.id},
        }
    }

    if venue.siret:
        venue_filter = {
            "or": [
                venue_filter,
                {
                    "filter": {
                        "attribute": {"name": "custom_fields." + ZendeskCustomFieldsShort.SIRET.value},
                        "parameter": {"eq": venue.siret},
                    }
                },
            ]
        }

    params = {
        "items": [
            {
                "data": {
                    "query": {
                        "filter": {
                            "and": [
                                {
                                    "filter": {
                                        "attribute": {"name": "is_organisation"},
                                        "parameter": {"eq": True},
                                    }
                                },
                                venue_filter,
                            ]
                        },
                        "projection": [
                            {"name": "id"},
                            {"name": f"custom_fields.{ZendeskCustomFieldsShort.SIRET.value}"},
                            {"name": f"custom_fields.{ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value}"},
                        ],
                    }
                }
            }
        ]
    }

    try:
        return _search_contact(params)
    except ContactFoundMoreThanOneError as e:
        contacts = e.items

        # looking for the item that has a product venue id amongst the found items
        contacts_with_venue_id = [
            contact
            for contact in contacts
            if contact["custom_fields"][ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value] == str(venue.id)
        ]

        # we found just one result, we assume it's the venue
        if len(contacts_with_venue_id) == 1:
            return contacts_with_venue_id[0]
        raise


def _get_parent_organization_id(venue: offerers_models.Venue) -> int | None:
    try:
        zendesk_offerer = get_offerer_by_id(venue.managingOfferer)
    except ContactFoundMoreThanOneError as e:
        for item in e.items:
            logger.warning(
                "Multiple results on Zendesk Sell search for offerer id %s",
                venue.managingOffererId,
                extra={
                    "sell_id ": item["id"],
                    "offerer_id": item["custom_fields"][ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value],
                    "siren": item["custom_fields"][ZendeskCustomFieldsShort.SIREN.value],
                },
            )
        return None
    except ContactNotFoundError:
        if not FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
            return None
        new_zendesk_offerer = zendesk_create_offerer(venue.managingOfferer)
        return new_zendesk_offerer["id"]
    else:
        return zendesk_offerer["id"]


def _get_venue_status(venue: offerers_models.Venue) -> str:
    if venue.collectiveOffers or venue.offers:
        if venue.nApprovedOffers > 0:
            return "Acteur Inscrit Actif"
        return "Acteur Inscrit non Actif"
    return "Acteur en cours d'inscription"


def zendesk_create_offerer(offerer: offerers_models.Offerer) -> dict:
    data = _get_offerer_data(offerer, created=True)
    return _query_api("POST", "/v2/contacts", body=data)


def zendesk_update_offerer(zendesk_id: int, offerer: offerers_models.Offerer) -> dict:
    data = _get_offerer_data(offerer)
    return _query_api("PUT", f"/v2/contacts/{zendesk_id}", body=data)


def zendesk_create_venue(venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
    if parent_organization_id == SEARCH_PARENT:
        parent_organization_id = _get_parent_organization_id(venue)

    data = _get_venue_data(venue, parent_organization_id, created=True)
    return _query_api("POST", "/v2/contacts", body=data)


def zendesk_update_venue(zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
    if parent_organization_id == SEARCH_PARENT:
        parent_organization_id = _get_parent_organization_id(venue)

    data = _get_venue_data(venue, parent_organization_id)
    return _query_api("PUT", f"/v2/contacts/{zendesk_id}", body=data)


def _stub_in_test_env(action: str, data: offerers_models.Offerer | offerers_models.Venue) -> bool:
    if settings.IS_RUNNING_TESTS:
        testing.zendesk_sell_requests.append({"action": action, "type": type(data).__name__, "id": data.id})
        return True

    if not settings.IS_PROD:
        logger.info("A request to Zendesk Sell API would be sent to %s %s %d", action, type(data).__name__, data.id)
        return True

    return False


def create_venue(venue: offerers_models.Venue) -> None:
    if not FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
        return

    if venue.isVirtual:
        return

    # API calls to Zendesk Sell are delayed in a GCP task to return quickly
    zendesk_sell_tasks.create_venue_task.delay(zendesk_sell_tasks.VenuePayload(venue_id=venue.id))


def do_create_venue(venue_id: int) -> None:
    """Called asynchronously by GCP task"""
    venue = offerers_repository.find_venue_by_id(venue_id)
    if not venue:
        logger.error("Trying to create venue which does not exist", extra={"venue_id": venue_id})
        return

    if _stub_in_test_env("create", venue):
        return

    try:
        zendesk_create_venue(venue, SEARCH_PARENT)
    except requests.exceptions.HTTPError as err:
        logger.error("Error while creating venue on Zendesk Sell", extra={"venue_id": venue.id, "error": err})


def update_venue(venue: offerers_models.Venue) -> None:
    if venue.isVirtual:
        return

    # API calls to Zendesk Sell are delayed in a GCP task to return quickly
    zendesk_sell_tasks.update_venue_task.delay(zendesk_sell_tasks.VenuePayload(venue_id=venue.id))


def do_update_venue(venue_id: int) -> None:
    """Called asynchronously by GCP task"""
    venue = offerers_repository.find_venue_by_id(venue_id)
    if not venue:
        logger.error("Trying to update venue which does not exist", extra={"venue_id": venue_id})
        return

    if _stub_in_test_env("update", venue):
        return

    try:
        try:
            zendesk_venue_data = get_venue_by_id(venue)
        except ContactFoundMoreThanOneError as err:
            logger.warning("Error while updating venue in Zendesk Sell: %s", err, extra={"venue_id": venue.id})
        except ContactNotFoundError:
            if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
                zendesk_create_venue(venue, SEARCH_PARENT)
        else:
            zendesk_venue_id = zendesk_venue_data["id"]
            zendesk_update_venue(zendesk_venue_id, venue, SEARCH_PARENT)
    except requests.exceptions.HTTPError as err:
        logger.error("Error while updating venue on Zendesk Sell", extra={"venue_id": venue.id, "error": err})


def create_offerer(offerer: offerers_models.Offerer) -> None:
    if not FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
        return

    if is_offerer_only_virtual(offerer):
        return

    # API calls to Zendesk Sell are delayed in a GCP task to return quickly
    zendesk_sell_tasks.create_offerer_task.delay(zendesk_sell_tasks.OffererPayload(offerer_id=offerer.id))


def do_create_offerer(offerer_id: int) -> None:
    """Called asynchronously by GCP task"""
    offerer = offerers_repository.find_offerer_by_id(offerer_id)
    if not offerer:
        logger.error("Trying to create offerer which does not exist", extra={"offerer_id": offerer_id})
        return

    if _stub_in_test_env("create", offerer):
        return

    try:
        zendesk_create_offerer(offerer)
    except requests.exceptions.HTTPError as err:
        logger.error("Error while creating offerer on Zendesk Sell", extra={"offerer_id": offerer.id, "error": err})


def update_offerer(offerer: offerers_models.Offerer) -> None:
    if is_offerer_only_virtual(offerer):
        return

    # API calls to Zendesk Sell are delayed in a GCP task to return quickly
    zendesk_sell_tasks.update_offerer_task.delay(zendesk_sell_tasks.OffererPayload(offerer_id=offerer.id))


def do_update_offerer(offerer_id: int) -> None:
    """Called asynchronously by GCP task"""
    offerer = offerers_repository.find_offerer_by_id(offerer_id)
    if not offerer:
        logger.error("Trying to update offerer which does not exist", extra={"offerer_id": offerer_id})
        return

    if _stub_in_test_env("update", offerer):
        return

    try:
        try:
            zendesk_offerer_data = get_offerer_by_id(offerer)
        except ContactFoundMoreThanOneError as err:
            logging.warning("Error while updating offerer in Zendesk Sell: %s", err, extra={"offerer_id": offerer.id})
        except ContactNotFoundError:
            if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
                zendesk_create_offerer(offerer)
        else:
            zendesk_offerer_id = zendesk_offerer_data["id"]
            zendesk_update_offerer(zendesk_offerer_id, offerer)
    except requests.exceptions.HTTPError as err:
        logger.error("Error while updating offerer on Zendesk Sell", extra={"offerer_id": offerer.id, "error": err})
