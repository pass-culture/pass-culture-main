import pytest

from pcapi.core.booking_providers.factories import BookingProviderFactory
from pcapi.core.booking_providers.factories import VenueBookingProviderFactory
from pcapi.core.booking_providers.models import BookingProviderName
from pcapi.core.external_bookings.api import _get_booking_provider_client_api
from pcapi.core.external_bookings.api import _get_venue_booking_provider
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
from pcapi.core.providers.factories import CDSCinemaDetailsFactory
from pcapi.core.providers.factories import CinemaProviderPivotFactory


@pytest.mark.usefixtures("db_session")
class GetBookingProviderTest:
    def test_should_return_booking_provider_according_to_venue_id(self) -> None:
        # Given
        booking_provider = BookingProviderFactory(name=BookingProviderName.CINE_DIGITAL_SERVICE, apiUrl="api_url_test")
        venue_booking_provider = VenueBookingProviderFactory(
            token="test_token", idAtProvider="test_id", bookingProvider=booking_provider
        )
        venue_id = venue_booking_provider.venueId

        # When
        assert _get_venue_booking_provider(venue_id) == venue_booking_provider

    def test_should_raise_exception_if_no_booking_provider(self) -> None:
        # Given
        venue_id = 0

        # When
        with pytest.raises(Exception) as e:
            _get_venue_booking_provider(venue_id)

        # Then
        assert str(e.value) == f"No active booking provider found for venue #{venue_id}"


@pytest.mark.usefixtures("db_session")
class GetBookingProviderClientApiTest:
    def test_should_return_client_api_according_to_name(self) -> None:
        # Given
        booking_provider = BookingProviderFactory(name=BookingProviderName.CINE_DIGITAL_SERVICE, apiUrl="test_api_url")
        venue_booking_provider = VenueBookingProviderFactory(idAtProvider="test_id", bookingProvider=booking_provider)
        cinema_provider_pivot = CinemaProviderPivotFactory(
            venue=venue_booking_provider.venue, idAtProvider=venue_booking_provider.idAtProvider
        )
        CDSCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaApiToken="test_token", accountId="test_account"
        )

        # When
        venue_id = venue_booking_provider.venueId
        client_api = _get_booking_provider_client_api(venue_id)

        # Then
        assert isinstance(client_api, CineDigitalServiceAPI)
        assert client_api.cinema_id == "test_id"
        assert client_api.token == "test_token"
        assert client_api.api_url == "test_api_url"

    def test_should_raise_an_exception_if_no_cds_details_provided_when_required(self) -> None:
        # Given
        booking_provider = BookingProviderFactory(name=BookingProviderName.CINE_DIGITAL_SERVICE, apiUrl="test_api_url")
        venue_booking_provider = VenueBookingProviderFactory(
            idAtProvider="test_id", bookingProvider=booking_provider, token=None
        )
        CinemaProviderPivotFactory(venue=venue_booking_provider.venue, idAtProvider=venue_booking_provider.idAtProvider)
        venue_id = venue_booking_provider.venueId

        # When
        with pytest.raises(Exception) as e:
            _get_booking_provider_client_api(venue_id)

        # Then
        assert str(e.value) == "No row was found when one was required"
