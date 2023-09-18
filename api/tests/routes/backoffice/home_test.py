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
    pytest.mark.backoffice,
]


class HomePageTest:
    # - session
    # - authenticated user
    # - user again to show the name
    # - data inserted in cards (stats got in a single request)
    expected_num_queries = 4

    def test_view_home_page_as_anonymous(self, client):
        response = client.get(url_for("backoffice_web.home"))
        assert response.status_code == 200

    def test_view_home_page(self, authenticated_client):
        response = authenticated_client.get(url_for("backoffice_web.home"))
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
            response = authenticated_client.get(url_for("backoffice_web.home"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert cards_text == [
            "2 offres individuelles en attente CONSULTER",
            "3 offres collectives en attente CONSULTER",
            "4 offres collectives vitrine en attente CONSULTER",
        ]
        # No card for "structure en attente de conformité" because tag "conformité" does not exist

    def test_view_home_page_pending_offerers_conformite(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory(name="conformité", label="En attente de conformité")
        other_tag = offerers_factories.OffererTagFactory()

        offerers_factories.PendingOffererFactory(tags=[tag, other_tag])

        # others should not be counted
        offerers_factories.NotValidatedOffererFactory(tags=[tag])
        offerers_factories.OffererFactory(tags=[tag])
        offerers_factories.NotValidatedOffererFactory(tags=[other_tag])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.home"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert cards_text == [
            "0 offre individuelle en attente CONSULTER",
            "0 offre collective en attente CONSULTER",
            "0 offre collective vitrine en attente CONSULTER",
            "1 structure en attente de conformité CONSULTER",
        ]
