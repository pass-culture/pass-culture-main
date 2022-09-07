import urllib.parse

import pytest
import requests_mock

from pcapi import settings
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users.external import zendesk_sell


pytestmark = pytest.mark.usefixtures("db_session")


def test_create_offerer():
    offerer = offerers_factories.OffererFactory(postalCode="95300")

    with requests_mock.Mocker() as mock:
        posted = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v2/contacts"), status_code=200, json={"id": "test"}
        )
        response = zendesk_sell.zendesk_create_offerer(offerer)

    assert posted.call_count == 1
    posted_json = posted.last_request.json()
    assert posted_json["data"]["is_organization"] is True
    assert posted_json["data"]["name"] == offerer.name
    assert posted_json["data"]["address"] == {
        "line1": offerer.address,
        "city": offerer.city,
        "postal_code": offerer.postalCode,
    }
    assert posted_json["data"]["custom_fields"]["Département"] == "95"
    assert posted_json["data"]["custom_fields"]["Région"] == "ILE-DE-FRANCE"
    assert posted_json["data"]["custom_fields"]["Typage"] == ["Structure"]
    assert posted_json["data"]["custom_fields"]["Produit Offerer ID"] == offerer.id
    assert posted_json["data"]["custom_fields"]["SIREN"] == offerer.siren
    assert posted_json["data"]["custom_fields"]["Créé depuis produit"] is True
    assert response["id"] == "test"


def test_update_offerer():
    zendesk_id = 12
    offerer = offerers_factories.OffererFactory(postalCode="20000")

    with requests_mock.Mocker() as mock:
        put = mock.put(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, f"/v2/contacts/{zendesk_id}"),
            status_code=200,
            json={"id": zendesk_id},
        )
        response = zendesk_sell.zendesk_update_offerer(zendesk_id, offerer)

    assert put.call_count == 1
    put_json = put.last_request.json()
    assert put_json["data"]["is_organization"] is True
    assert put_json["data"]["name"] == offerer.name
    assert put_json["data"]["address"] == {
        "line1": offerer.address,
        "city": offerer.city,
        "postal_code": offerer.postalCode,
    }
    assert put_json["data"]["custom_fields"]["Département"] == "20"
    assert put_json["data"]["custom_fields"]["Région"] == "CORSE"
    assert put_json["data"]["custom_fields"]["Typage"] == ["Structure"]
    assert put_json["data"]["custom_fields"]["Produit Offerer ID"] == offerer.id
    assert put_json["data"]["custom_fields"]["SIREN"] == offerer.siren
    assert "Créé depuis produit" not in put_json["data"]["custom_fields"]

    assert response["id"] == zendesk_id


def test_create_venue():
    zendesk_parent_id = 123
    venue = offerers_factories.VenueFactory(postalCode="97600")
    offers_factories.ThingOfferFactory(venue=venue, isActive=False)

    with requests_mock.Mocker() as mock:
        searched = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v3/contacts/search"),
            status_code=200,
            json={"items": [{"meta": {"total_count": 1}, "items": [{"data": {"id": zendesk_parent_id}}]}]},
        )
        posted = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v2/contacts"), status_code=200, json={"id": "test"}
        )
        response = zendesk_sell.zendesk_create_venue(venue, zendesk_sell.SEARCH_PARENT)

    assert searched.call_count == 1
    searched_json = searched.last_request.json()
    assert searched_json

    assert posted.call_count == 1
    posted_json = posted.last_request.json()
    assert posted_json["data"]["is_organization"] is True
    assert posted_json["data"]["name"] == venue.name
    assert posted_json["data"]["parent_organization_id"] == zendesk_parent_id
    assert posted_json["data"]["email"] == venue.bookingEmail
    assert posted_json["data"]["phone"] == venue.contact.phone_number
    assert posted_json["data"]["address"] == {
        "line1": venue.address,
        "city": venue.city,
        "postal_code": venue.postalCode,
    }
    assert posted_json["data"]["custom_fields"]["Département"] == "976"
    assert posted_json["data"]["custom_fields"]["Région"] == "MAYOTTE"
    assert posted_json["data"]["custom_fields"]["Typage"] == ["Lieu"]
    assert posted_json["data"]["custom_fields"]["Produit Venue ID"] == venue.id
    assert posted_json["data"]["custom_fields"]["SIRET"] == venue.siret
    assert posted_json["data"]["custom_fields"]["Statut PC Pro"] == "Acteur Inscrit Actif"
    assert posted_json["data"]["custom_fields"]["Créé depuis produit"] is True

    assert response["id"] == "test"


def test_update_venue():
    zendesk_parent_id = 100
    zendesk_id = 200

    venue = offerers_factories.VenueFactory(postalCode="98600", contact=None)  # Wallis-et-Futuna

    with requests_mock.Mocker() as mock:
        searched = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v3/contacts/search"),
            status_code=200,
            json={"items": [{"meta": {"total_count": 1}, "items": [{"data": {"id": zendesk_parent_id}}]}]},
        )
        put = mock.put(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, f"/v2/contacts/{zendesk_id}"),
            status_code=200,
            json={"id": zendesk_id},
        )
        response = zendesk_sell.zendesk_update_venue(zendesk_id, venue, zendesk_sell.SEARCH_PARENT)

    assert searched.call_count == 1
    searched_json = searched.last_request.json()
    assert searched_json

    assert put.call_count == 1
    put_json = put.last_request.json()
    assert put_json["data"]["is_organization"] is True
    assert put_json["data"]["name"] == venue.name
    assert put_json["data"]["parent_organization_id"] == zendesk_parent_id
    assert put_json["data"]["email"] == venue.bookingEmail
    assert put_json["data"]["phone"] is None
    assert put_json["data"]["address"] == {
        "line1": venue.address,
        "city": venue.city,
        "postal_code": venue.postalCode,
    }
    assert put_json["data"]["custom_fields"]["Département"] == "986"
    assert put_json["data"]["custom_fields"]["Région"] == "Aucune valeur"
    assert put_json["data"]["custom_fields"]["Typage"] == ["Lieu"]
    assert put_json["data"]["custom_fields"]["Produit Venue ID"] == venue.id
    assert put_json["data"]["custom_fields"]["SIRET"] == venue.siret
    assert put_json["data"]["custom_fields"]["Statut PC Pro"] == "Acteur en cours d'inscription"
    assert "Créé depuis produit" not in put_json["data"]["custom_fields"]

    assert response["id"] == zendesk_id


@override_features(ENABLE_ZENDESK_SELL_CREATION=False)
def test_create_venue_without_parent_offerer():
    # Offerer is not found in Zendesk, but feature flag prevents from creating it
    ret_id = 10
    offerer = offerers_factories.OffererFactory(postalCode="97100")
    venue = offerers_factories.VenueFactory(postalCode="97200", managingOfferer=offerer)
    offers_factories.ThingOfferFactory(venue=venue, isActive=False)

    with requests_mock.Mocker() as mock:
        searched = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v3/contacts/search"),
            status_code=200,
            json={"items": [{"meta": {"total_count": 0}, "items": []}]},
        )
        posted = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v2/contacts"), status_code=200, json={"id": ret_id}
        )
        response = zendesk_sell.zendesk_create_venue(venue, zendesk_sell.SEARCH_PARENT)

    assert searched.call_count == 1
    searched_json = searched.last_request.json()
    assert searched_json

    assert posted.call_count == 1

    posted_venue_json = posted.last_request.json()
    assert posted_venue_json["data"]["is_organization"] is True
    assert posted_venue_json["data"]["name"] == venue.name
    assert posted_venue_json["data"]["parent_organization_id"] is None  # No parent created
    assert posted_venue_json["data"]["email"] == venue.bookingEmail
    assert posted_venue_json["data"]["phone"] == venue.contact.phone_number
    assert posted_venue_json["data"]["address"] == {
        "line1": venue.address,
        "city": venue.city,
        "postal_code": venue.postalCode,
    }
    assert posted_venue_json["data"]["custom_fields"]["Département"] == "972"
    assert posted_venue_json["data"]["custom_fields"]["Région"] == "MARTINIQUE"
    assert posted_venue_json["data"]["custom_fields"]["Typage"] == ["Lieu"]
    assert posted_venue_json["data"]["custom_fields"]["Produit Venue ID"] == venue.id
    assert posted_venue_json["data"]["custom_fields"]["SIRET"] == venue.siret
    assert posted_venue_json["data"]["custom_fields"]["Statut PC Pro"] == "Acteur Inscrit Actif"

    assert response["id"] == ret_id


@override_features(ENABLE_ZENDESK_SELL_CREATION=True)
def test_create_venue_and_parent_offerer():
    # Offerer is not found in Zendesk, create it before the venue
    ret_id = 10
    offerer = offerers_factories.OffererFactory(postalCode="97100")
    venue = offerers_factories.VenueFactory(postalCode="97200", managingOfferer=offerer)
    offers_factories.ThingOfferFactory(venue=venue, isActive=False)

    with requests_mock.Mocker() as mock:
        searched = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v3/contacts/search"),
            status_code=200,
            json={"items": [{"meta": {"total_count": 0}, "items": []}]},
        )
        posted = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v2/contacts"), status_code=200, json={"id": ret_id}
        )
        response = zendesk_sell.zendesk_create_venue(venue, zendesk_sell.SEARCH_PARENT)

    assert searched.call_count == 1
    searched_json = searched.last_request.json()
    assert searched_json

    assert posted.call_count == 2

    posted_offerer_json = posted.request_history[0].json()
    assert posted_offerer_json["data"]["is_organization"] is True
    assert posted_offerer_json["data"]["name"] == offerer.name
    assert posted_offerer_json["data"]["address"] == {
        "line1": offerer.address,
        "city": offerer.city,
        "postal_code": offerer.postalCode,
    }
    assert posted_offerer_json["data"]["custom_fields"]["Département"] == "971"
    assert posted_offerer_json["data"]["custom_fields"]["Région"] == "GUADELOUPE"
    assert posted_offerer_json["data"]["custom_fields"]["Typage"] == ["Structure"]
    assert posted_offerer_json["data"]["custom_fields"]["Produit Offerer ID"] == offerer.id
    assert posted_offerer_json["data"]["custom_fields"]["SIREN"] == offerer.siren
    assert posted_offerer_json["data"]["custom_fields"]["Créé depuis produit"] is True

    posted_venue_json = posted.request_history[1].json()
    assert posted_venue_json["data"]["is_organization"] is True
    assert posted_venue_json["data"]["name"] == venue.name
    assert posted_venue_json["data"]["parent_organization_id"] == ret_id
    assert posted_venue_json["data"]["email"] == venue.bookingEmail
    assert posted_venue_json["data"]["phone"] == venue.contact.phone_number
    assert posted_venue_json["data"]["address"] == {
        "line1": venue.address,
        "city": venue.city,
        "postal_code": venue.postalCode,
    }
    assert posted_venue_json["data"]["custom_fields"]["Département"] == "972"
    assert posted_venue_json["data"]["custom_fields"]["Région"] == "MARTINIQUE"
    assert posted_venue_json["data"]["custom_fields"]["Typage"] == ["Lieu"]
    assert posted_venue_json["data"]["custom_fields"]["Produit Venue ID"] == venue.id
    assert posted_venue_json["data"]["custom_fields"]["SIRET"] == venue.siret
    assert posted_venue_json["data"]["custom_fields"]["Statut PC Pro"] == "Acteur Inscrit Actif"

    assert response["id"] == ret_id


@override_settings(IS_RUNNING_TESTS=False, IS_PROD=True, ZENDESK_SELL_API_KEY="test")
def test_update_offerer_multiple_results_none_has_id():
    offerer = offerers_factories.OffererFactory()

    with requests_mock.Mocker() as mock:
        searched = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v3/contacts/search"),
            status_code=200,
            json={
                "items": [
                    {
                        "meta": {"total_count": 2},
                        "items": [
                            {
                                "data": {
                                    "id": 1,
                                    "custom_fields": {
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: None
                                    },
                                }
                            },
                            {
                                "data": {
                                    "id": 2,
                                    "custom_fields": {
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: None
                                    },
                                }
                            },
                        ],
                    }
                ]
            },
        )
        put = mock.put(requests_mock.ANY, status_code=200, json={})
        zendesk_sell.do_update_offerer(offerer.id)

    assert searched.call_count == 1
    assert put.call_count == 0  # nothing updated in Zendesk


@override_settings(IS_RUNNING_TESTS=False, IS_PROD=True, ZENDESK_SELL_API_KEY="test")
def test_update_offerer_multiple_results_one_has_id():
    offerer = offerers_factories.OffererFactory()

    with requests_mock.Mocker() as mock:
        searched = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v3/contacts/search"),
            status_code=200,
            json={
                "items": [
                    {
                        "meta": {"total_count": 2},
                        "items": [
                            {
                                "data": {
                                    "id": 1,
                                    "custom_fields": {
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: None,
                                        zendesk_sell.ZendeskCustomFieldsShort.SIREN.value: offerer.siren,
                                    },
                                }
                            },
                            {
                                "data": {
                                    "id": 2,
                                    "custom_fields": {
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: str(offerer.id),
                                        zendesk_sell.ZendeskCustomFieldsShort.SIREN.value: None,
                                    },
                                }
                            },
                        ],
                    }
                ]
            },
        )
        put = mock.put(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v2/contacts/2"),
            status_code=200,
            json={"id": 2},
        )
        zendesk_sell.do_update_offerer(offerer.id)

    assert searched.call_count == 1
    assert put.call_count == 1


@override_settings(IS_RUNNING_TESTS=False, IS_PROD=True, ZENDESK_SELL_API_KEY="test")
def test_update_venue_multiple_results_none_has_id():
    venue = offerers_factories.VenueFactory()

    with requests_mock.Mocker() as mock:
        searched = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v3/contacts/search"),
            status_code=200,
            json={
                "items": [
                    {
                        "meta": {"total_count": 2},
                        "items": [
                            {
                                "data": {
                                    "id": 1,
                                    "custom_fields": {
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value: None
                                    },
                                }
                            },
                            {
                                "data": {
                                    "id": 2,
                                    "custom_fields": {
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value: None
                                    },
                                }
                            },
                        ],
                    }
                ]
            },
        )
        put = mock.put(requests_mock.ANY, status_code=200, json={})
        zendesk_sell.do_update_venue(venue.id)

    assert searched.call_count == 1
    assert put.call_count == 0  # nothing updated in Zendesk


@override_settings(IS_RUNNING_TESTS=False, IS_PROD=True, ZENDESK_SELL_API_KEY="test")
def test_update_venue_multiple_results_one_has_id():
    venue = offerers_factories.VenueFactory()

    with requests_mock.Mocker() as mock:
        searched = mock.post(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v3/contacts/search"),
            status_code=200,
            json={
                "items": [
                    {
                        "meta": {"total_count": 2},
                        "items": [
                            {
                                "data": {
                                    "id": 1,
                                    "custom_fields": {
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: None,
                                        zendesk_sell.ZendeskCustomFieldsShort.SIREN.value: None,
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value: str(venue.id),
                                    },
                                }
                            },
                            {
                                "data": {
                                    "id": 2,
                                    "custom_fields": {
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: None,
                                        zendesk_sell.ZendeskCustomFieldsShort.SIREN.value: None,
                                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value: str(venue.id + 1),
                                    },
                                }
                            },
                        ],
                    }
                ]
            },
        )
        put = mock.put(
            urllib.parse.urljoin(settings.ZENDESK_SELL_API_URL, "/v2/contacts/1"),
            status_code=200,
            json={"id": 1},
        )
        zendesk_sell.do_update_venue(venue.id)

    assert searched.call_count == 2  # venue and managing offerer
    assert put.call_count == 1
