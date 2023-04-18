import pytest

from pcapi.core.external_bookings.api import _get_external_bookings_client_api
from pcapi.core.external_bookings.api import get_active_cinema_venue_provider
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class


@pytest.mark.usefixtures("db_session")
class GetCinemaVenueProviderTest:
    def test_should_return_cinema_venue_provider_according_to_venue_id(self) -> None:
        # Given
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
        providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)

        venue_id = venue_provider.venueId

        # When
        assert get_active_cinema_venue_provider(venue_id) == venue_provider

    def test_should_raise_exception_if_no_cinema_venue_provider(self) -> None:
        # Given
        venue_id = 0

        # When
        with pytest.raises(providers_exceptions.InactiveProvider) as exc:
            get_active_cinema_venue_provider(venue_id)

        # Then
        assert str(exc.value) == f"No active cinema venue provider found for venue #{venue_id}"

    def test_should_raise_exception_if_inactive_cinema_venue_provider(self) -> None:
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider, isActive=False)
        providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)

        venue_id = venue_provider.venueId
        with pytest.raises(providers_exceptions.InactiveProvider) as e:
            get_active_cinema_venue_provider(venue_id)

        assert str(e.value) == f"No active cinema venue provider found for venue #{venue_id}"


@pytest.mark.usefixtures("db_session")
class GetExternalBookingsClientApiTest:
    def test_should_return_client_api_according_to_name(self) -> None:
        # Given
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            provider=cds_provider, venueIdAtOfferProvider="test_id"
        )
        cinema_provider_pivot = providers_factories.CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaApiToken="test_token", accountId="test_account"
        )

        # When
        venue_id = venue_provider.venueId
        client_api = _get_external_bookings_client_api(venue_id)

        # Then
        assert isinstance(client_api, CineDigitalServiceAPI)
        assert client_api.cinema_id == "test_id"
        assert client_api.token == "test_token"
        assert client_api.account_id == "test_account"
        assert client_api.api_url == "test_cds_url/vad/"

    def test_should_raise_an_exception_if_no_cds_details_provided_when_required(self) -> None:
        # Given
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            provider=cds_provider, venueIdAtOfferProvider="test_id"
        )
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )

        # When
        venue_id = venue_provider.venueId
        with pytest.raises(Exception) as e:
            _get_external_bookings_client_api(venue_id)

        # Then
        assert str(e.value) == "No row was found when one was required"
