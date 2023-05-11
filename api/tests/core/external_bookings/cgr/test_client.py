import json

import pytest

from pcapi.connectors.cgr.exceptions import CGRAPIException
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.external_bookings.cgr.client as cgr_client
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures


@pytest.mark.usefixtures("db_session")
class BookTicketTest:
    def test_should_book_one_ticket(self, requests_mock, app):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=1, amount=5.5)
        venue_id = booking.venueId
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://cgr-cinema-0.example.com/web_service"
        )
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.get(
            "http://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )
        post_adapter = requests_mock.post(
            "http://cgr-cinema-0.example.com/web_service",
            text=fixtures.cgr_reservation_response_template(fixtures.ONE_TICKET_RESPONSE),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id)
        tickets = cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert len(tickets) == 1
        assert tickets[0].barcode == "CINE999508637111"
        assert tickets[0].seat_number == "D8"
        assert post_adapter.call_count == 1
        assert "<pNBPlaces>1</pNBPlaces>" in post_adapter.last_request.text
        assert "<pEmail>beneficiary@example.com</pEmail>" in post_adapter.last_request.text
        assert "<pPUTTC>5.50</pPUTTC>" in post_adapter.last_request.text
        assert "<pIDSeances>177182</pIDSeances>" in post_adapter.last_request.text
        redis_external_bookings = app.redis_client.lrange("api:external_bookings:barcodes", 0, -1)
        assert len(redis_external_bookings) == 1
        external_booking_info = json.loads(redis_external_bookings[0])
        assert external_booking_info["barcode"] == "CINE999508637111"
        assert external_booking_info["venue_id"] == venue_id
        assert external_booking_info["timestamp"]

    def test_should_book_one_ticket_when_placement_is_disabled(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=1, amount=5.5)
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://cgr-cinema-0.example.com/web_service"
        )
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.get(
            "http://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )
        post_adapter = requests_mock.post(
            "http://cgr-cinema-0.example.com/web_service",
            text=fixtures.cgr_reservation_response_template(fixtures.ONE_TICKET_RESPONSE_WITHOUT_PLACEMENT),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id)
        tickets = cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert len(tickets) == 1
        assert tickets[0].barcode == "CINE999508637111"
        assert not tickets[0].seat_number
        assert post_adapter.call_count == 1
        assert "<pNBPlaces>1</pNBPlaces>" in post_adapter.last_request.text
        assert "<pEmail>beneficiary@example.com</pEmail>" in post_adapter.last_request.text
        assert "<pPUTTC>5.50</pPUTTC>" in post_adapter.last_request.text
        assert "<pIDSeances>177182</pIDSeances>" in post_adapter.last_request.text

    def test_should_book_two_tickets(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2, amount=5.5)
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://cgr-cinema-0.example.com/web_service"
        )
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.get(
            "http://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )
        post_adapter = requests_mock.post(
            "http://cgr-cinema-0.example.com/web_service",
            text=fixtures.cgr_reservation_response_template(fixtures.TWO_TICKETS_RESPONSE),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id)
        tickets = cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert len(tickets) == 2
        assert tickets[0].barcode == "CINE999508637111"
        assert tickets[0].seat_number == "F7"
        assert tickets[1].barcode == "CINE999508637111"
        assert tickets[1].seat_number == "F8"
        assert post_adapter.call_count == 1
        assert "<pNBPlaces>2</pNBPlaces>" in post_adapter.last_request.text
        assert "<pEmail>beneficiary@example.com</pEmail>" in post_adapter.last_request.text
        assert "<pPUTTC>5.50</pPUTTC>" in post_adapter.last_request.text
        assert "<pIDSeances>177182</pIDSeances>" in post_adapter.last_request.text

    def test_should_book_two_tickets_when_placement_is_disabled(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2, amount=5.5)
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://cgr-cinema-0.example.com/web_service"
        )
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.get(
            "http://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )

        post_adapter = requests_mock.post(
            "http://cgr-cinema-0.example.com/web_service",
            text=fixtures.cgr_reservation_response_template(fixtures.TWO_TICKETS_RESPONSE_WITHOUT_PLACEMENT),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id)
        tickets = cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert len(tickets) == 2
        assert tickets[0].barcode == "CINE999508637111"
        assert not tickets[0].seat_number
        assert tickets[1].barcode == "CINE999508637111"
        assert not tickets[1].seat_number
        assert post_adapter.call_count == 1
        assert "<pNBPlaces>2</pNBPlaces>" in post_adapter.last_request.text
        assert "<pEmail>beneficiary@example.com</pEmail>" in post_adapter.last_request.text
        assert "<pPUTTC>5.50</pPUTTC>" in post_adapter.last_request.text
        assert "<pIDSeances>177182</pIDSeances>" in post_adapter.last_request.text


@pytest.mark.usefixtures("db_session")
class CancelBookingTest:
    def test_should_cancel_booking_with_success(self, requests_mock):
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="https://cinema-0.example.com/web_service"
        )
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get("https://cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        post_adapter = requests_mock.post(
            "https://cinema-0.example.com/web_service",
            text=fixtures.cgr_annulation_response_template(),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_str_id)
        try:
            cgr.cancel_booking(barcodes=["CINE-123456789"])
        except CGRAPIException:
            assert False, "Should not raise exception"

        assert post_adapter.call_count == 1
        assert "<pQrCode>CINE-123456789</pQrCode>" in post_adapter.last_request.text

    def test_when_cgr_returns_element_not_found(self, requests_mock):
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="https://cinema-0.example.com/web_service"
        )
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get("https://cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "https://cinema-0.example.com/web_service",
            text=fixtures.cgr_annulation_response_template(
                success=False,
                message_error="L'annulation n'a pas pu être prise en compte : Code barre non reconnu / annulation impossible",
            ),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id)
        with pytest.raises(CGRAPIException) as exception:
            cgr.cancel_booking(barcodes=["CINE-987654321"])

        assert (
            str(exception.value)
            == "Error on CGR API on AnnulationPassCulture : L'annulation n'a pas pu être prise en compte : Code barre non reconnu / annulation impossible"
        )
