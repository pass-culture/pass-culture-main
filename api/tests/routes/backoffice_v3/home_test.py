from base64 import b64encode

from flask import url_for
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import offer_mixin

from .helpers import html_parser


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class HomePageTest:
    # - session
    # - authenticated user
    # - user again to show the name
    # - data inserted in cards (stats got in a single request)
    expected_num_queries = 4

    def test_view_home_page_as_anonymous(self, client):
        response = client.get(url_for("backoffice_v3_web.home"))
        assert response.status_code == 200

    def test_view_home_page(self, authenticated_client):
        response = authenticated_client.get(url_for("backoffice_v3_web.home"))
        assert response.status_code == 200

    def test_view_home_page_pending_offers(self, authenticated_client):
        validated_venue = offerers_factories.VenueFactory()
        not_validated_venue = offerers_factories.VenueFactory(
            managingOfferer=offerers_factories.NotValidatedOffererFactory()
        )

        # pending offers from validated offerers
        offers_factories.OfferFactory.create_batch(
            2, validation=offer_mixin.OfferValidationStatus.PENDING, venue=validated_venue
        )
        educational_factories.CollectiveOfferFactory.create_batch(
            3, validation=offer_mixin.OfferValidationStatus.PENDING, venue=validated_venue
        )
        educational_factories.CollectiveOfferTemplateFactory.create_batch(
            4, validation=offer_mixin.OfferValidationStatus.PENDING, venue=validated_venue
        )

        # others should not be counted
        offers_factories.OfferFactory(venue=validated_venue)
        offers_factories.OfferFactory(validation=offer_mixin.OfferValidationStatus.PENDING, venue=not_validated_venue)
        educational_factories.CollectiveOfferFactory(venue=validated_venue)
        educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.PENDING, venue=not_validated_venue
        )
        educational_factories.CollectiveOfferTemplateFactory(venue=validated_venue)
        educational_factories.CollectiveOfferTemplateFactory(
            validation=offer_mixin.OfferValidationStatus.PENDING, venue=not_validated_venue
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_v3_web.home"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert cards_text == [
            "2 offres individuelles en attente CONSULTER",
            "3 offres collectives en attente CONSULTER",
            "4 offres collectives vitrine en attente CONSULTER",
        ]

    def test_redirect_authenticated_user(self, authenticated_client):
        dummy_url = url_for("backoffice_v3_web.collective_offer.list_collective_offers")
        base64_dummy_url = b64encode(dummy_url.encode())
        response = authenticated_client.get(url_for("backoffice_v3_web.home", redirect=base64_dummy_url))
        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.collective_offer.list_collective_offers", _external=True)

    def test_transmit_redirect_unauthenticated_user(self, client):
        dummy_url = url_for("backoffice_v3_web.collective_offer.list_collective_offers")
        base64_dummy_url = b64encode(dummy_url.encode())
        response = client.get(url_for("backoffice_v3_web.home", redirect=base64_dummy_url))
        assert response.status_code == 200
        assert base64_dummy_url in response.data
