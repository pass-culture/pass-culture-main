from unittest.mock import patch

from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.factories import UserFactory

from tests.conftest import TestClient
from tests.conftest import clean_database


class VenueViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_venue_siret(self, mocked_validate_csrf_token, app):
        UserFactory(email="user@example.com", isAdmin=True)
        venue = VenueFactory(siret="22222222222222")
        old_id_at_providers = "11111@22222222222222"
        stock = StockFactory(
            offer__venue=venue, idAtProviders=old_id_at_providers, offer__idAtProviders=old_id_at_providers
        )

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

        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue_edited = Venue.query.get(venue.id)
        stock_edited = Stock.query.get(stock.id)
        offer_edited = Offer.query.get(stock.offer.id)

        assert venue_edited.siret == "88888888888888"
        assert stock_edited.idAtProviders == "11111@88888888888888"
        assert offer_edited.idAtProviders == "11111@88888888888888"

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_venue_other_offer_id_at_provider(self, mocked_validate_csrf_token, app):
        UserFactory(email="user@example.com", isAdmin=True)
        venue = VenueFactory(siret="22222222222222")
        id_at_providers = "id_at_provider_ne_contenant_pas_le_siret"
        stock = StockFactory(offer__venue=venue, idAtProviders=id_at_providers, offer__idAtProviders=id_at_providers)

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

        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue_edited = Venue.query.get(venue.id)
        stock = Stock.query.get(stock.id)
        offer = Offer.query.get(stock.offer.id)

        assert venue_edited.siret == "88888888888888"
        assert stock.idAtProviders == "id_at_provider_ne_contenant_pas_le_siret"
        assert offer.idAtProviders == "id_at_provider_ne_contenant_pas_le_siret"

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_venue_without_siret(self, mocked_validate_csrf_token, app):
        UserFactory(email="user@example.com", isAdmin=True)
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

        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302
