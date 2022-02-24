from unittest.mock import patch

import pytest

from pcapi.admin.custom_views.venue_view import _get_venue_provider_link
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers import factories as providers_factories
from pcapi.core.users.factories import AdminFactory

from tests.conftest import TestClient
from tests.conftest import clean_database


class VenueViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_update_venue_siret(self, mocked_async_index_offers_of_venue_ids, mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = VenueFactory(siret="22222222222222")
        id_at_provider = "11111"
        old_id_at_providers = f"{id_at_provider}@{venue.siret}"
        stock = StockFactory(offer__venue=venue, idAtProviders=old_id_at_providers, offer__idAtProvider=id_at_provider)

        data = dict(
            name=venue.name,
            siret="88888888888888",
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude=venue.latitude,
            longitude=venue.longitude,
            isPermanent=venue.isPermanent,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue_edited = Venue.query.get(venue.id)
        stock_edited = Stock.query.get(stock.id)

        assert venue_edited.siret == "88888888888888"
        assert stock_edited.idAtProviders == "11111@88888888888888"

        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_venue_other_offer_id_at_provider(self, mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = VenueFactory(siret="22222222222222")
        id_at_providers = "id_at_provider_ne_contenant_pas_le_siret"
        stock = StockFactory(offer__venue=venue, idAtProviders=id_at_providers, offer__idAtProvider=id_at_providers)

        data = dict(
            name=venue.name,
            siret="88888888888888",
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude=venue.latitude,
            longitude=venue.longitude,
            isPermanent=venue.isPermanent,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue_edited = Venue.query.get(venue.id)
        stock = Stock.query.get(stock.id)
        offer = Offer.query.get(stock.offer.id)

        assert venue_edited.siret == "88888888888888"
        assert stock.idAtProviders == "id_at_provider_ne_contenant_pas_le_siret"
        assert offer.idAtProvider == "id_at_provider_ne_contenant_pas_le_siret"

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_venue_without_siret(self, mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = VenueFactory(siret=None, comment="comment to allow null siret")

        data = dict(
            name=venue.name,
            siret="88888888888888",
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude=venue.latitude,
            longitude=venue.longitude,
            isPermanent=venue.isPermanent,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_update_venue_reindex_all(self, mocked_async_index_offers_of_venue_ids, mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = VenueFactory(isPermanent=False)

        new_name = venue.name + "(updated)"
        data = dict(
            name=new_name,
            siret=venue.siret,
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude="42.01",
            longitude=venue.longitude,
            isPermanent=True,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue = Venue.query.get(venue.id)
        assert venue.isPermanent
        assert venue.name == new_name

        mocked_async_index_offers_of_venue_ids.assert_called_once_with([venue.id])

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_update_venue_reindex_venue_only(
        self, mocked_async_index_venue_ids, mocked_async_index_offers_of_venue_ids, mocked_validate_csrf_token, app
    ):
        AdminFactory(email="user@example.com")
        venue = VenueFactory(isPermanent=False)

        data = dict(
            name=venue.name,
            siret=venue.siret,
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude=venue.latitude,
            longitude=venue.longitude,
            isPermanent=True,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue = Venue.query.get(venue.id)
        assert venue.isPermanent

        mocked_async_index_venue_ids.assert_called_once_with([venue.id])
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    @patch("pcapi.core.search.async_index_venue_ids")
    @patch("pcapi.core.search.reindex_venue_ids")
    def test_reindex_when_tags_updated(
        self,
        mocked_reindex_venue_ids,
        mocked_async_index_venue_ids,
        mocked_async_index_offers_of_venue_ids,
        mocked_validate_csrf_token,
        client,
    ):
        admin = AdminFactory(email="user@example.com")
        venue = VenueFactory(isPermanent=True)
        tag = offers_factories.CriterionFactory()
        data = {
            "criteria": [tag.id],
            "name": venue.name,
            "siret": venue.siret,
            "city": venue.city,
            "postalCode": venue.postalCode,
            "address": venue.address,
            "publicName": venue.publicName,
            "latitude": venue.latitude,
            "longitude": venue.longitude,
            "isPermanent": True,
        }

        client = client.with_session_auth(admin.email)
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        mocked_reindex_venue_ids.assert_called_once_with([venue.id])
        mocked_async_index_venue_ids.assert_not_called()
        mocked_async_index_offers_of_venue_ids.assert_not_called()


class GetVenueProviderLinkTest:
    @pytest.mark.usefixtures("db_session")
    def test_return_empty_link_when_no_venue_provider(self, app):
        # Given
        venue = VenueFactory()

        # When
        link = _get_venue_provider_link(None, None, venue, None)

        # Then
        assert not link

    @pytest.mark.usefixtures("db_session")
    def test_return_link_to_venue_provider(self, app):
        # Given
        venue_provider = providers_factories.VenueProviderFactory()
        venue = venue_provider.venue

        # When
        link = _get_venue_provider_link(None, None, venue, None)

        # Then
        assert str(venue.id) in link
