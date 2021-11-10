from unittest.mock import patch

from pcapi.admin.custom_views.venue_provider_view import VenueProviderView
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offerers.factories import AllocineProviderFactory
from pcapi.core.offerers.factories import AllocineVenueProviderFactory
from pcapi.core.offerers.factories import AllocineVenueProviderPriceRuleFactory
from pcapi.core.offerers.factories import ProviderFactory
from pcapi.core.offerers.factories import VenueProviderFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.factories import AdminFactory

from tests.conftest import clean_database


class VenueProviderViewTest:
    def test_prevent_access_not_authenticated(self, app, db_session):
        # When
        view = VenueProviderView(VenueProvider, db_session)

        # Then
        assert not view.is_accessible()

    @patch("pcapi.admin.base_configuration.current_user")
    def test_prevent_access_missing_venue_access(self, current_user, app, db_session):
        # Given
        current_user.is_authenticated = True
        current_user.isAdmin = False

        # When
        view = VenueProviderView(VenueProvider, db_session)

        # Then
        assert not view.is_accessible()


class EditModelTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.workers.venue_provider_job.synchronize_venue_provider")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def test_edit_venue_provider(
        self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, validate_csrf_token, client, app
    ):
        # Given
        AdminFactory(email="user@example.com")
        venue = VenueFactory()
        old_provider = ProviderFactory(
            name="old provider", enabledForPro=True, localClass=None, apiUrl="https://example.com"
        )
        new_provider = ProviderFactory(
            name="new provider", enabledForPro=True, localClass=None, apiUrl="https://example2.com"
        )
        venue_provider = VenueProviderFactory(provider=old_provider, venue=venue)

        existing_stock = StockFactory(quantity=10, offer__venue=venue, offer__idAtProviders="1")
        BookingFactory(stock=existing_stock)

        mock_siret_can_be_synchronized.return_value = True

        data = dict(
            provider=new_provider.id,
            venue=venue.id,
            venueIdAtOfferProvider="hsf4uiagèy12386dq",
        )

        client.with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue_providers/edit/?id={venue_provider.id}", form=data)

        assert response.status_code == 302

        # Then
        venue_provider = VenueProvider.query.one()

        # Check that venue_provider model have been updated
        assert venue_provider.venue == venue
        assert venue_provider.provider == new_provider
        assert venue_provider.venueIdAtOfferProvider == "hsf4uiagèy12386dq"

        # Check that the quantity of existing stocks have been updated and quantity reset to booked_quantity.
        assert existing_stock.quantity == 1
        assert existing_stock.offer.lastProviderId == new_provider.id

        mock_synchronize_venue_provider.assert_called_once_with(venue_provider)

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def test_provider_not_synchronizable(self, mock_siret_can_be_synchronized, validate_csrf_token, client):
        # Given
        AdminFactory(email="user@example.com")
        venue = VenueFactory()
        old_provider = ProviderFactory(enabledForPro=True, localClass=None, apiUrl="https://example.com")
        new_provider = ProviderFactory(enabledForPro=True, localClass=None, apiUrl="https://example2.com")
        venue_provider = VenueProviderFactory(provider=old_provider, venue=venue, venueIdAtOfferProvider="old-siret")

        mock_siret_can_be_synchronized.return_value = False

        data = dict(
            provider=new_provider.id,
            venue=venue.id,
            venueIdAtOfferProvider="hsf4uiagèy12386dq",
        )

        client.with_session_auth("user@example.com")
        client.post(f"/pc/back-office/venue_providers/edit/?id={venue_provider.id}", form=data)

        # Then
        assert venue_provider.provider == old_provider
        assert venue_provider.venueIdAtOfferProvider == "old-siret"

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.workers.venue_provider_job.synchronize_venue_provider")
    def test_allocine_provider(self, synchronize_venue_provider, validate_csrf_token, client):
        # Given
        AdminFactory(email="user@example.com")
        venue = VenueFactory(siret="siret-pivot")
        provider = AllocineProviderFactory(enabledForPro=True)

        venue_provider = AllocineVenueProviderFactory(provider=provider, venue=venue, isDuo=False, quantity=111)
        AllocineVenueProviderPriceRuleFactory(price=11, allocineVenueProvider=venue_provider)

        data = dict(
            isDuo=True,
            allocine_price=22,
            allocine_quantity=222,
            provider=provider.id,
            venue=venue.id,
            venueIdAtOfferProvider="ABCDEF12345",
        )

        client.with_session_auth("user@example.com")
        client.post(f"/pc/back-office/venue_providers/edit/?id={venue_provider.id}", form=data)
        synchronize_venue_provider.assert_called_once_with(venue_provider)

        # Then
        assert venue.venueProviders[0] == venue_provider
        assert venue_provider.quantity == 222
