import pytest

from pcapi.core.educational.adage_backends.adage import AdageHttpClient
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
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
        booking = CollectiveBookingFactory()
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
        booking = CollectiveBookingFactory()
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
        booking = CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        # When
        requests_mock.post(f"{MOCK_API_URL}/v1/prereservation", status_code=500)
        with pytest.raises(AdageException):
            adage_client.notify_prebooking(booking_data)

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_institution_association_success_if_201(self, requests_mock):
        # Given
        adage_client = AdageHttpClient()
        offer = CollectiveOfferFactory(
            institution=EducationalInstitutionFactory(), collectiveStock=CollectiveStockFactory()
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
        offer = CollectiveOfferFactory(
            institution=EducationalInstitutionFactory(), collectiveStock=CollectiveStockFactory()
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
        offer = CollectiveOfferFactory(
            institution=EducationalInstitutionFactory(), collectiveStock=CollectiveStockFactory()
        )
        offer_data = serialize_collective_offer(offer)

        # When
        requests_mock.post(f"{MOCK_API_URL}/v1/offre-assoc", status_code=500)
        with pytest.raises(AdageException):
            adage_client.notify_institution_association(offer_data)
