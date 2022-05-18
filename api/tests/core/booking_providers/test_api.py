from datetime import datetime
from typing import Any
from unittest.mock import patch

import pytest

from pcapi.connectors.serialization.cine_digital_service_serializers import IdObjectCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowTariffCDS
from pcapi.core.booking_providers.api import _get_booking_provider_client_api
from pcapi.core.booking_providers.api import _get_venue_booking_provider
from pcapi.core.booking_providers.api import get_show_stock
from pcapi.core.booking_providers.cds.client import CineDigitalServiceAPI
from pcapi.core.booking_providers.factories import BookingProviderFactory
from pcapi.core.booking_providers.factories import VenueBookingProviderFactory
from pcapi.core.booking_providers.models import BookingProviderName


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
        venue_booking_provider = VenueBookingProviderFactory(
            token="test_token", idAtProvider="test_id", bookingProvider=booking_provider
        )
        venue_id = venue_booking_provider.venueId

        # When
        client_api = _get_booking_provider_client_api(venue_id)

        # Then
        assert isinstance(client_api, CineDigitalServiceAPI)
        assert client_api.cinema_id == "test_id"
        assert client_api.token == "test_token"
        assert client_api.api_url == "test_api_url"

    def test_should_raise_an_exception_if_no_token_provided_when_required(self) -> None:
        # Given
        booking_provider = BookingProviderFactory(name=BookingProviderName.CINE_DIGITAL_SERVICE, apiUrl="test_api_url")
        venue_booking_provider = VenueBookingProviderFactory(
            idAtProvider="test_id", bookingProvider=booking_provider, token=None
        )
        venue_id = venue_booking_provider.venueId

        # When
        with pytest.raises(Exception) as e:
            _get_booking_provider_client_api(venue_id)

        # Then
        assert str(e.value) == f"Missing token for {venue_booking_provider.idAtProvider}"


@pytest.mark.usefixtures("db_session")
class GetShowStockTest:
    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_show")
    def test_should_return_avaible_places_for_show_id(self, mocked_show: Any) -> None:
        # Given
        booking_provider = BookingProviderFactory(name=BookingProviderName.CINE_DIGITAL_SERVICE, apiUrl="api_url_test")
        venue_booking_provider = VenueBookingProviderFactory(bookingProvider=booking_provider)
        venue_id = venue_booking_provider.venueId
        mocked_show.return_value = ShowCDS(
            id=1,
            canceled=False,
            deleted=False,
            internetremainingplace=15,
            showtime=datetime.utcnow(),
            showsTariffPostypeCollection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
            screenid=IdObjectCDS(id=2),
        )

        # When
        remaining_places = get_show_stock(venue_id, 1)

        # Then
        assert remaining_places == 15
