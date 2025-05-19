from unittest import mock

import pytest
from flask import url_for

from pcapi.core.external.zendesk_sell_backends import base as zendesk_sell
from pcapi.core.external.zendesk_sell_backends import testing as zendesk_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import testing
from pcapi.utils import requests

from .helpers import html_parser
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class UpdateOffererOnZendeskSellTest(PostEndpointHelper):
    endpoint = "backoffice_web.zendesk_sell.update_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_sync_offerer(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)

        assert testing.zendesk_sell_requests == [
            {
                "action": "update",
                "type": "Offerer",
                "id": offerer.id,
                "zendesk_id": zendesk_testing.TESTING_ZENDESK_ID_OFFERER,
            }
        ]

    def test_sync_only_virtual_offerer(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Cette entité juridique ne gère que des partenaires culturels virtuels"
        )

        assert not testing.zendesk_sell_requests

    @mock.patch("pcapi.core.external.zendesk_sell_backends.testing.TestingBackend.get_offerer_by_id")
    def test_sync_offerer_matching_several_contacts(self, mock_get_offerer_by_id, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        mock_get_offerer_by_id.side_effect = zendesk_sell.ContactFoundMoreThanOneError(
            [
                {
                    "id": "123",
                    "custom_fields": {
                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: offerer.id,
                        zendesk_sell.ZendeskCustomFieldsShort.SIREN.value: offerer.siren,
                    },
                },
                {
                    "id": "456",
                    "custom_fields": {
                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: offerer.id,
                        zendesk_sell.ZendeskCustomFieldsShort.SIREN.value: "",
                    },
                },
            ]
        )

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Plusieurs entités juridiques ont été trouvées dans Zendesk Sell, aucune ne peut donc être mise à jour : "
            f"Identifiant Zendesk Sell : 123, Produit Offerer ID : {offerer.id}, SIREN : {offerer.siren} "
            f"Identifiant Zendesk Sell : 456, Produit Offerer ID : {offerer.id}, SIREN :"
        )

        assert not testing.zendesk_sell_requests

    @mock.patch("pcapi.core.external.zendesk_sell_backends.testing.TestingBackend.get_offerer_by_id")
    def test_sync_offerer_not_found(self, mock_get_offerer_by_id, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        mock_get_offerer_by_id.side_effect = zendesk_sell.ContactNotFoundError()

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'entité juridique n'a pas été trouvée dans Zendesk Sell"
        )

        assert not testing.zendesk_sell_requests


class UpdateVenueOnZendeskSellTest(PostEndpointHelper):
    endpoint = "backoffice_web.zendesk_sell.update_venue"
    endpoint_kwargs = {"venue_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_sync_open_to_public_venue_with_parent(self, authenticated_client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

        assert testing.zendesk_sell_requests == [
            {
                "action": "update",
                "type": "Venue",
                "id": venue.id,
                "zendesk_id": zendesk_testing.TESTING_ZENDESK_ID_VENUE,
                "parent_organization_id": zendesk_testing.TESTING_ZENDESK_ID_OFFERER,
            },
        ]

    @mock.patch("pcapi.core.external.zendesk_sell_backends.testing.TestingBackend.get_offerer_by_id")
    def test_sync_open_to_public_venue_without_parent(self, mock_get_offerer_by_id, authenticated_client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)

        mock_get_offerer_by_id.side_effect = zendesk_sell.ContactNotFoundError()

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)

        assert testing.zendesk_sell_requests == [
            {
                "action": "update",
                "type": "Venue",
                "id": venue.id,
                "zendesk_id": zendesk_testing.TESTING_ZENDESK_ID_VENUE,
                "parent_organization_id": None,
            },
        ]

    @mock.patch("pcapi.core.external.zendesk_sell_backends.testing.TestingBackend.get_offerer_by_id")
    def test_sync_open_to_public_venue_with_two_parents(self, mock_get_offerer_by_id, authenticated_client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)

        mock_get_offerer_by_id.side_effect = zendesk_sell.ContactFoundMoreThanOneError(
            [
                {
                    "id": "123",
                    "custom_fields": {
                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: venue.managingOffererId,
                        zendesk_sell.ZendeskCustomFieldsShort.SIREN.value: venue.managingOfferer.siren,
                    },
                },
                {
                    "id": "456",
                    "custom_fields": {
                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value: venue.managingOffererId,
                        zendesk_sell.ZendeskCustomFieldsShort.SIREN.value: "",
                    },
                },
            ]
        )

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)
        assert html_parser.extract_alerts(authenticated_client.get(response.location).data) == [
            "Attention : Plusieurs entités juridiques parentes possibles ont été trouvées pour ce partenaire culturel dans Zendesk Sell. "
            f"Identifiant Zendesk Sell : 123, Produit Offerer ID : {venue.managingOffererId}, SIREN : {venue.managingOfferer.siren} "
            f"Identifiant Zendesk Sell : 456, Produit Offerer ID : {venue.managingOffererId}, SIREN :",
            "Le partenaire culturel a été mis à jour sur Zendesk Sell",
        ]

        assert testing.zendesk_sell_requests == [
            {
                "action": "update",
                "type": "Venue",
                "id": venue.id,
                "zendesk_id": zendesk_testing.TESTING_ZENDESK_ID_VENUE,
                "parent_organization_id": None,
            },
        ]

    @mock.patch("pcapi.core.external.zendesk_sell_backends.testing.TestingBackend.get_offerer_by_id")
    def test_sync_open_to_public_venue_with_parent_error(self, mock_get_offerer_by_id, authenticated_client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)

        response = requests.Response
        response.status_code = 500
        mock_get_offerer_by_id.side_effect = requests.exceptions.HTTPError("test", response=response)

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)
        assert html_parser.extract_alerts(authenticated_client.get(response.location).data) == [
            "Une erreur 500 s'est produite lors de la recherche de l'entité juridique parente : test",
            "Le partenaire culturel a été mis à jour sur Zendesk Sell",
        ]
        assert testing.zendesk_sell_requests == [
            {
                "action": "update",
                "type": "Venue",
                "id": venue.id,
                "zendesk_id": zendesk_testing.TESTING_ZENDESK_ID_VENUE,
                "parent_organization_id": None,
            },
        ]

    def test_sync_non_open_to_public_venue(self, authenticated_client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=False)

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Ce partenaire culturel est virtuel ou n'est pas ouvert au public"
        )

        assert not testing.zendesk_sell_requests

    def test_sync_virtual_venue(self, authenticated_client):
        venue = offerers_factories.VirtualVenueFactory()

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Ce partenaire culturel est virtuel ou n'est pas ouvert au public"
        )

        assert not testing.zendesk_sell_requests

    @mock.patch("pcapi.core.external.zendesk_sell_backends.testing.TestingBackend.get_venue_by_id")
    def test_sync_venue_matching_several_contacts(self, mock_get_venue_by_id, authenticated_client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)

        mock_get_venue_by_id.side_effect = zendesk_sell.ContactFoundMoreThanOneError(
            [
                {
                    "id": "123",
                    "custom_fields": {
                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value: venue.id,
                        zendesk_sell.ZendeskCustomFieldsShort.SIRET.value: venue.siret,
                    },
                },
                {
                    "id": "456",
                    "custom_fields": {
                        zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value: venue.id,
                        zendesk_sell.ZendeskCustomFieldsShort.SIRET.value: "",
                    },
                },
            ]
        )

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Plusieurs partenaires culturels ont été trouvés dans Zendesk Sell, aucun ne peut donc être mis à jour : "
            f"Identifiant Zendesk Sell : 123, Produit Venue ID : {venue.id}, SIRET : {venue.siret} "
            f"Identifiant Zendesk Sell : 456, Produit Venue ID : {venue.id}, SIRET :"
        )

        assert not testing.zendesk_sell_requests

    @mock.patch("pcapi.core.external.zendesk_sell_backends.testing.TestingBackend.get_venue_by_id")
    def test_sync_venue_not_found(self, mock_get_venue_by_id, authenticated_client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)

        mock_get_venue_by_id.side_effect = zendesk_sell.ContactNotFoundError()

        response = self.post_to_endpoint(authenticated_client, venue_id=venue.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.venue.get", venue_id=venue.id, _external=True)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le partenaire culturel n'a pas été trouvé dans Zendesk Sell"
        )

        assert not testing.zendesk_sell_requests
