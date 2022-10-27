import pytest

from pcapi.core.educational.adage_backends.adage import AdageHttpClient
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.models import AdageApiResult
from pcapi.core.testing import override_settings
from pcapi.routes.adage.v1.serialization import prebooking


MOCK_API_URL = "http://adage.fr"


class AdageHttpClientTest:
    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_returns_result_if_adage_answers_201_response_code(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        booking = CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        response_data = {"result": "ok"}
        requests_mock.post(f"{MOCK_API_URL}/v1/prereservation", status_code=201, json=response_data)

        # When
        result = adage_client.notify_prebooking(booking_data)

        # Then
        assert isinstance(result, AdageApiResult)
        assert result.success == True
        assert result.response == response_data

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_returns_result_if_adage_answers_404_response_code(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        booking = CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        response_data = {"result": "EMAIL_ADDRESS_DOES_NOT_EXIST"}
        requests_mock.post(f"{MOCK_API_URL}/v1/prereservation", status_code=404, json=response_data)

        # When
        result = adage_client.notify_prebooking(booking_data)

        # Then
        assert isinstance(result, AdageApiResult)
        assert result.success == True
        assert result.response == response_data

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_raises_if_adage_answers_error_response_code(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        booking = CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        requests_mock.post(f"{MOCK_API_URL}/v1/prereservation", status_code=500)

        # When
        with pytest.raises(AdageException):
            adage_client.notify_prebooking(booking_data)
