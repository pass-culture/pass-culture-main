import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.adage_backends.adage import AdageHttpClient
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer_request
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.testing import override_settings
from pcapi.routes.adage.v1.serialization import prebooking


MOCK_API_URL = "http://adage.fr"
ADAGE_RESPONSE_FOR_INSTITUTION_WITHOUT_EMAIL = {
    "type": "http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html",
    "title": "Not Found",
    "status": 404,
    "detail": "EMAIL_ADDRESS_DOES_NOT_EXIST",
}


@pytest.mark.usefixtures("db_session")
class AdageHttpClientTest:
    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_success_if_201(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        booking = educational_factories.CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        # When
        endpoint = requests_mock.post(f"{MOCK_API_URL}/v1/prereservation", status_code=201)
        adage_client.notify_prebooking(booking_data)

        # Then
        assert endpoint.called

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_success_if_404(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        booking = educational_factories.CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        # When
        requests_mock.post(
            f"{MOCK_API_URL}/v1/prereservation", status_code=404, json=ADAGE_RESPONSE_FOR_INSTITUTION_WITHOUT_EMAIL
        )

        # When
        adage_client.notify_prebooking(booking_data)

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_raises_if_500(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        booking = educational_factories.CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        # When
        requests_mock.post(f"{MOCK_API_URL}/v1/prereservation", status_code=500)
        with pytest.raises(AdageException):
            adage_client.notify_prebooking(booking_data)

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_institution_association_success_if_201(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        offer = educational_factories.CollectiveOfferFactory(
            institution=educational_factories.EducationalInstitutionFactory(),
            collectiveStock=educational_factories.CollectiveStockFactory(),
        )
        offer_data = serialize_collective_offer(offer)

        # When
        endpoint = requests_mock.post(f"{MOCK_API_URL}/v1/offre-assoc", status_code=201)
        adage_client.notify_institution_association(offer_data)

        # Then
        assert endpoint.called

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_institution_association_success_if_404(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        offer = educational_factories.CollectiveOfferFactory(
            institution=educational_factories.EducationalInstitutionFactory(),
            collectiveStock=educational_factories.CollectiveStockFactory(),
        )
        offer_data = serialize_collective_offer(offer)

        # When
        endpoint = requests_mock.post(
            f"{MOCK_API_URL}/v1/offre-assoc", status_code=404, json=ADAGE_RESPONSE_FOR_INSTITUTION_WITHOUT_EMAIL
        )
        adage_client.notify_institution_association(offer_data)

        # Then
        assert endpoint.called

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_institution_association_raises_if_500(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        offer = educational_factories.CollectiveOfferFactory(
            institution=educational_factories.EducationalInstitutionFactory(),
            collectiveStock=educational_factories.CollectiveStockFactory(),
        )
        offer_data = serialize_collective_offer(offer)

        # When
        requests_mock.post(f"{MOCK_API_URL}/v1/offre-assoc", status_code=500)
        with pytest.raises(AdageException):
            adage_client.notify_institution_association(offer_data)

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_redactor_when_collective_request_is_made_success_if_201(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        request = educational_factories.CollectiveOfferRequestFactory()
        request_data = serialize_collective_offer_request(request)

        # When
        endpoint = requests_mock.post(f"{MOCK_API_URL}/v1/offre-vitrine", status_code=201)
        adage_client.notify_redactor_when_collective_request_is_made(request_data)

        # Then
        assert endpoint.called
