import datetime
import json
import logging
import urllib.parse

from pcapi import settings
from pcapi.core.external.zendesk_sell_backends.base import BaseBackend
from pcapi.core.external.zendesk_sell_backends.base import ContactFoundMoreThanOneError
from pcapi.core.external.zendesk_sell_backends.base import ContactNotFoundError
from pcapi.core.external.zendesk_sell_backends.base import ZendeskCustomFieldsNames
from pcapi.core.external.zendesk_sell_backends.base import ZendeskCustomFieldsShort
from pcapi.core.offerers import models as offerers_models
from pcapi.utils import requests
from pcapi.utils import urls
from pcapi.utils.regions import get_region_name_from_department


logger = logging.getLogger(__name__)


ZENDESK_SELL_API_KEY = settings.ZENDESK_SELL_API_KEY
ZENDESK_SELL_API_URL = settings.ZENDESK_SELL_API_URL


class ZendeskSellReadOnlyBackend(BaseBackend):
    def __init__(self) -> None:
        self.session = self._configure_session()

    def create_offerer(self, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        return {"id": None}

    def update_offerer(self, zendesk_id: int, offerer: offerers_models.Offerer) -> dict:
        return {"id": None}

    def create_venue(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        return {"id": None}

    def update_venue(self, zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
        return {"id": None}

    def search_contact(self, params: dict) -> dict:
        body = self.query_api("POST", "/v3/contacts/search", body=params)

        # Response format:
        # https://developer.zendesk.com/api-reference/sales-crm/search/response/

        item_dict = list(body.values())[0][0]
        total_count: int = item_dict["meta"]["total_count"]  # how many results for the query string

        if total_count == 1:
            return item_dict["items"][0]["data"]
        if total_count > 1:
            raise ContactFoundMoreThanOneError([item["data"] for item in item_dict["items"]])
        raise ContactNotFoundError

    def get_offerer_by_id(self, offerer: offerers_models.Offerer) -> dict:
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
                                                        "name": "custom_fields." + ZendeskCustomFieldsShort.TYPAGE.value
                                                    },
                                                    "parameter": {"eq": "Structure"},
                                                }
                                            },
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
                                                    "attribute": {
                                                        "name": "custom_fields." + ZendeskCustomFieldsShort.SIRET.value
                                                    },
                                                    "parameter": {"is_null": True},
                                                }
                                            },
                                        ]
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
            return self.search_contact(params)
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

    def get_venue_by_id(self, venue: offerers_models.Venue) -> dict:
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
            return self.search_contact(params)
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


class ZendeskSellBackend(ZendeskSellReadOnlyBackend):
    def create_offerer(self, offerer: offerers_models.Offerer, created: bool = True) -> dict:
        response = {}
        data = self._get_offerer_data(offerer, created)
        try:
            response = self.query_api("POST", "/v2/contacts", data)
        except requests.exceptions.HTTPError as err:
            logger.error("Error while creating offerer on Zendesk Sell", extra={"offerer_id": offerer.id, "error": err})
        return response

    def update_offerer(self, zendesk_id: int, offerer: offerers_models.Offerer) -> dict:
        response = {}
        data = self._get_offerer_data(offerer)
        try:
            response = self.query_api("PUT", f"/v2/contacts/{zendesk_id}", data)
        except requests.exceptions.HTTPError as err:
            logger.error("Error while updating offerer on Zendesk Sell", extra={"offerer_id": offerer.id, "error": err})
        return response

    def create_venue(
        self, venue: offerers_models.Venue, parent_organization_id: int | None, created: bool = True
    ) -> dict:
        response = {}
        data = self._get_venue_data(venue, parent_organization_id, created)
        try:
            response = self.query_api("POST", "/v2/contacts", data)
        except requests.exceptions.HTTPError as err:
            logger.error("Error while creating venue on Zendesk Sell", extra={"venue_id": venue.id, "error": err})
        return response

    def update_venue(self, zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
        response = {}
        data = self._get_venue_data(venue, parent_organization_id)
        try:
            response = self.query_api("PUT", f"/v2/contacts/{zendesk_id}", data)
        except requests.exceptions.HTTPError as err:
            logger.error("Error while udpating venue on Zendesk Sell", extra={"venue_id": venue.id, "error": err})
        return response

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
                "last_name": "",  # leave that empty for the Zendesk api
                "description": venue.description,
                "industry": venue.venueTypeCode.value,
                "website": venue.contact.website if venue.contact else None,
                "email": venue.bookingEmail,
                "phone": venue.contact.phone_number if venue.contact else None,
                "twitter": social_medias.get("twitter", ""),
                "facebook": social_medias.get("facebook", ""),
                "address": {
                    "line1": venue.street,
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
                    ZendeskCustomFieldsNames.BACKOFFICE_LINK.value: urls.build_backoffice_venue_link(venue.id),
                    ZendeskCustomFieldsNames.UPDATED_IN_PRODUCT.value: datetime.datetime.utcnow().isoformat(),
                },
            }
        }

        if parent_organization_id:
            # Do not remove potential parent in Zendesk in case we have two matching parents
            params["data"]["parent_organization_id"] = parent_organization_id

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
                    "line1": offerer.street,
                    "city": offerer.city,
                    "postal_code": offerer.postalCode,
                },
                "custom_fields": {
                    ZendeskCustomFieldsNames.DEPARTEMENT.value: offerer.departementCode,
                    ZendeskCustomFieldsNames.INTERNAL_COMMENT.value: "Mis à jour par le produit le %s"
                    % (datetime.date.today().strftime("%d/%m/%Y"),),
                    ZendeskCustomFieldsNames.JURIDIC_NAME.value: offerer.name,
                    ZendeskCustomFieldsNames.PRODUCT_OFFERER_ID.value: offerer.id,
                    ZendeskCustomFieldsNames.REGION.value: get_region_name_from_department(
                        offerer.departementCode
                    ).upper(),
                    ZendeskCustomFieldsNames.SIREN.value: offerer.siren,
                    ZendeskCustomFieldsNames.TYPAGE.value: ["Structure"],
                    ZendeskCustomFieldsNames.BACKOFFICE_LINK.value: urls.build_backoffice_offerer_link(offerer.id),
                    ZendeskCustomFieldsNames.UPDATED_IN_PRODUCT.value: datetime.datetime.utcnow().isoformat(),
                },
            }
        }

        if created:
            params["data"]["custom_fields"][ZendeskCustomFieldsNames.CREATED_FROM_PRODUCT.value] = True

        return params
