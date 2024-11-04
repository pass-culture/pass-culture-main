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

ADAGE_RESPONSE_FOR_ERROR = {
    "type": "http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html",
    "title": "Error",
    "status": 500,
    "detail": "ERROR",
}


@pytest.mark.usefixtures("db_session")
class AdageHttpClientTest:
    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_success_if_201(self, requests_mock):
        adage_client = AdageHttpClient()
        booking = educational_factories.CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        endpoint = requests_mock.post(f"{MOCK_API_URL}/v1/prereservation", status_code=201)
        adage_client.notify_prebooking(booking_data)

        assert endpoint.called

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_success_if_404(self, requests_mock):
        adage_client = AdageHttpClient()
        booking = educational_factories.CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        requests_mock.post(
            f"{MOCK_API_URL}/v1/prereservation", status_code=404, json=ADAGE_RESPONSE_FOR_INSTITUTION_WITHOUT_EMAIL
        )

        adage_client.notify_prebooking(booking_data)

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_prebooking_raises_if_500(self, requests_mock):
        adage_client = AdageHttpClient()
        booking = educational_factories.CollectiveBookingFactory()
        booking_data = prebooking.serialize_collective_booking(booking)

        requests_mock.post(f"{MOCK_API_URL}/v1/prereservation", status_code=500, json=ADAGE_RESPONSE_FOR_ERROR)
        with pytest.raises(AdageException) as ex:
            adage_client.notify_prebooking(booking_data)

        assert ex.value.message == "Error posting new prebooking to Adage API - status code: 500 - error code: ERROR"

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_institution_association_success_if_201(self, requests_mock):
        adage_client = AdageHttpClient()
        offer = educational_factories.CollectiveOfferFactory(
            institution=educational_factories.EducationalInstitutionFactory(),
            collectiveStock=educational_factories.CollectiveStockFactory(),
        )
        offer_data = serialize_collective_offer(offer)

        endpoint = requests_mock.post(f"{MOCK_API_URL}/v1/offre-assoc", status_code=201)
        adage_client.notify_institution_association(offer_data)

        assert endpoint.called

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_institution_association_success_if_404(self, requests_mock):
        adage_client = AdageHttpClient()
        offer = educational_factories.CollectiveOfferFactory(
            institution=educational_factories.EducationalInstitutionFactory(),
            collectiveStock=educational_factories.CollectiveStockFactory(),
        )
        offer_data = serialize_collective_offer(offer)

        endpoint = requests_mock.post(
            f"{MOCK_API_URL}/v1/offre-assoc", status_code=404, json=ADAGE_RESPONSE_FOR_INSTITUTION_WITHOUT_EMAIL
        )
        adage_client.notify_institution_association(offer_data)

        assert endpoint.called

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_notify_institution_association_raises_if_500(self, requests_mock):
        adage_client = AdageHttpClient()
        offer = educational_factories.CollectiveOfferFactory(
            institution=educational_factories.EducationalInstitutionFactory(),
            collectiveStock=educational_factories.CollectiveStockFactory(),
        )
        offer_data = serialize_collective_offer(offer)

        requests_mock.post(f"{MOCK_API_URL}/v1/offre-assoc", status_code=500, json=ADAGE_RESPONSE_FOR_ERROR)
        with pytest.raises(AdageException) as ex:
            adage_client.notify_institution_association(offer_data)

        assert ex.value.message == "Error getting Adage API - status code: 500 - error code: ERROR"

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_api_error_invalid_json(self, requests_mock):
        adage_client = AdageHttpClient()
        offer = educational_factories.CollectiveOfferFactory(
            institution=educational_factories.EducationalInstitutionFactory(),
            collectiveStock=educational_factories.CollectiveStockFactory(),
        )
        offer_data = serialize_collective_offer(offer)

        requests_mock.post(f"{MOCK_API_URL}/v1/offre-assoc", status_code=500, json=None)
        with pytest.raises(AdageException) as ex:
            adage_client.notify_institution_association(offer_data)

        assert ex.value.message == "Error while reading Adage API json response - status code: 500"

    @override_settings(ADAGE_API_URL=MOCK_API_URL)
    def test_redactor_when_collective_request_is_made_success_if_201(self, requests_mock):
        adage_client = AdageHttpClient()
        request = educational_factories.CollectiveOfferRequestFactory()
        request_data = serialize_collective_offer_request(request)

        endpoint = requests_mock.post(f"{MOCK_API_URL}/v1/offre-vitrine", status_code=201)
        adage_client.notify_redactor_when_collective_request_is_made(request_data)

        assert endpoint.called
