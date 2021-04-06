from unittest.mock import patch

import pytest

from pcapi.admin.custom_views.venue_provider_view import VenueProviderView
from pcapi.admin.custom_views.venue_view import _get_venue_provider_link
from pcapi.core.offerers.factories import VenueProviderFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.models import VenueProvider


class VenueProviderViewTest:
    def test_prevent_access_not_authenticated(self, app, db_session):
        # When
        view = VenueProviderView(VenueProvider, db_session)

        # Then
        assert view.is_accessible() is False

    @patch("pcapi.admin.base_configuration.current_user")
    def test_prevent_access_missing_venue_access(self, current_user, app, db_session):
        # Given
        current_user.is_authenticated = True
        current_user.isAdmin = True

        # When
        view = VenueProviderView(VenueProvider, db_session)

        # Then
        assert view.is_accessible() is False

    @patch("pcapi.admin.base_configuration.current_user")
    @patch("pcapi.admin.custom_views.venue_provider_view.request.args.get")
    def test_allow_access_with_venue_id(self, get, current_user, app, db_session):
        # Given
        get.return_value = 12
        current_user.is_authenticated = True
        current_user.isAdmin = True

        # When
        view = VenueProviderView(VenueProvider, db_session)

        # Then
        assert view.is_accessible() is True


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
        assert f"{venue.id}" in link
        assert "venue_providers" in link
