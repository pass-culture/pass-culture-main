from unittest.mock import patch

import pytest

from pcapi.admin.custom_views.venue_provider_view import VenueProviderView
from pcapi.admin.custom_views.venue_view import _get_venue_provider_link
from pcapi.core.offerers.factories import ProviderFactory
from pcapi.core.offerers.factories import VenueProviderFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.models import VenueProvider


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


class CreateModelTest:
    @patch("pcapi.core.providers.api._check_venue_can_be_synchronized_with_provider", lambda *args, **kwargs: True)
    @patch("pcapi.workers.venue_provider_job.synchronize_venue_provider")
    def test_use_api_method_to_create_venue_provider(self, synchronize_venue_provider, db_session):
        # Given
        venue = VenueFactory()
        provider = ProviderFactory(enabledForPro=True, localClass=None, apiUrl="https://example.com")
        view = VenueProviderView(VenueProvider, db_session)
        VenueProviderForm = view.scaffold_form()

        data = dict(
            isDuo=True,
            price=23.5,
            provider=provider,
            venueId=venue.id,
            venueIdAtOfferProvider="hsf4uiagèy12386dq",
        )
        form = VenueProviderForm(data=data)

        # When
        view.create_model(form)

        # Then
        venue_provider = VenueProvider.query.one()
        assert venue_provider.venue == venue
        assert venue_provider.provider == provider
        assert venue_provider.venueIdAtOfferProvider == "hsf4uiagèy12386dq"
        synchronize_venue_provider.assert_called_once_with(venue_provider)


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
        venue_provider = VenueProviderFactory()
        venue = venue_provider.venue

        # When
        link = _get_venue_provider_link(None, None, venue, None)

        # Then
        assert str(venue.id) in link
        assert "venue_providers" in link
