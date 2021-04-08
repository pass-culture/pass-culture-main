from unittest.mock import patch

import pytest

from pcapi.admin.custom_views.venue_provider_view import VenueProviderView
from pcapi.admin.custom_views.venue_view import _get_venue_provider_link
from pcapi.core.offerers.factories import VenueProviderFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.models import VenueProvider
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.utils.human_ids import humanize


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
        current_user.isAdmin = False

        # When
        view = VenueProviderView(VenueProvider, db_session)

        # Then
        assert view.is_accessible() is False


class CreateModelTest:
    @patch("pcapi.admin.custom_views.venue_provider_view.api.create_venue_provider")
    def test_use_api_method_to_create_venue_provider(self, create_venue_provider, app, db_session):
        # Given
        venue = VenueFactory()
        provider = activate_provider("TiteLiveStocks")
        view = VenueProviderView(VenueProvider, db_session)
        VenueProviderForm = view.scaffold_form()

        data = dict(
            isDuo=True, price=23.5, provider=provider, venueId=venue.id, venueIdAtOfferProvider="hsf4uiagèy12386dq"
        )
        form = VenueProviderForm(data=data)

        # When
        view.create_model(form)

        # Then
        create_venue_provider.assert_called_once()
        create_venue_provider.assert_called_once_with(
            PostVenueProviderBody(
                venueId=humanize(venue.id),
                providerId=humanize(provider.id),
                price="23.5",
                isDuo=True,
                venueIdAtOfferProvider="hsf4uiagèy12386dq",
            )
        )


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
