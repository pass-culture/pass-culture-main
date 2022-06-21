import pytest
import requests_mock

from pcapi.core.bookings import factories as booking_factories
import pcapi.core.educational.adage_backends as adage_client
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.testing import override_settings
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_booking


@pytest.mark.usefixtures("db_session")
class AdageHttpClientTest:
    @override_settings(ADAGE_API_URL="https://adage-api-url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    @override_settings(ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient")
    def test_should_raise_AdageException_when_api_response_status_not_201(self):
        # Given
        booking = booking_factories.EducationalBookingFactory()

        # When
        with pytest.raises(AdageException) as exception:
            with requests_mock.Mocker() as request_mock:
                request_mock.post(
                    "https://adage-api-url/v1/prereservation",
                    request_headers={
                        "X-omogen-api-key": "adage-api-key",
                    },
                    status_code=406,
                )
                adage_client.notify_prebooking(data=serialize_educational_booking(booking.educationalBooking))

        # Then
        assert str(exception.value) == "Error posting new prebooking to Adage API."

    @override_settings(ADAGE_API_URL="https://adage-api-url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    @override_settings(ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient")
    def test_should_not_raise_exception_when_api_response_status_201(self):
        # Given
        booking = booking_factories.EducationalBookingFactory()
        expected_response = {"description": "created", "status_code": 201}

        # When
        with requests_mock.Mocker() as request_mock:
            request_mock.post(
                "https://adage-api-url/v1/prereservation",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                json=expected_response,
                status_code=201,
            )
            adage_api_result = adage_client.notify_prebooking(
                data=serialize_educational_booking(booking.educationalBooking)
            )

        # Then
        assert adage_api_result.success
        assert adage_api_result.response == expected_response
