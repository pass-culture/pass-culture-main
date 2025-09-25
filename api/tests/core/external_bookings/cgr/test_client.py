import json

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.external_bookings.cgr.client as cgr_client
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.external_bookings.cgr.exceptions import CGRAPIException
from pcapi.core.external_bookings.exceptions import ExternalBookingNotEnoughSeatsError
from pcapi.core.external_bookings.exceptions import ExternalBookingShowDoesNotExistError
from pcapi.utils.crypto import encrypt

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures


def _get_seances_pass_culture_xml_response_template(body_response: str) -> str:
    return f"""
       <?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
            <SOAP-ENV:Header/>
            <SOAP-ENV:Body>
                <ns1:GetSeancesPassCultureResponse xmlns:ns1="urn:GestionCinemaWS">
                    <GetSeancesPassCultureResult>
                        {body_response}
                    </GetSeancesPassCultureResult>
                </ns1:GetSeancesPassCultureResponse>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """.strip()


class GetCGRServiceProxyTest:
    def test_should_return_service_proxy(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)

        service = cgr_client._get_cgr_service_proxy(cinema_url="http://example.com/web_service")

        assert service._binding_options["address"] == "http://example.com/web_service"
        assert service._operations["GetSeancesPassCulture"]
        assert service._operations["ReservationPassCulture"]
        assert service._operations["AnnulationPassCulture"]


class GetSeancesPassCulture:
    @pytest.mark.settings(CGR_API_USER="pass_user")
    def test_should_raise_if_error(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        json_response = {"CodeErreur": -1, "IntituleErreur": "Expectation failed", "ObjetRetour": None}
        response = _get_seances_pass_culture_xml_response_template(json.dumps(json_response))
        requests_mock.post("http://example.com/web_service", text=response)
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/web_service")
        cinema_id = cgr_cinema_details.cinemaProviderPivot.idAtProvider
        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)

        with pytest.raises(CGRAPIException) as exc:
            cgr._get_seances_pass_culture()

        assert str(exc.value) == "Error on CGR API on GetSeancesPassCulture : Expectation failed"

    @pytest.mark.settings(CGR_API_USER="pass_user")
    def test_should_call_with_the_right_password(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        get_seances_adapter = requests_mock.post(
            "http://example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://example.com/web_service",
            password=encrypt("theRealPassword"),
        )
        cinema_id = cgr_cinema_details.cinemaProviderPivot.idAtProvider
        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)

        cgr._get_seances_pass_culture()

        assert "<mdp>theRealPassword</mdp>" in get_seances_adapter.last_request.text


@pytest.mark.usefixtures("db_session")
class GetFilmsTest:
    @pytest.mark.settings(CGR_API_USER="pass_user")
    def test_should_return_films(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "http://example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/web_service")
        cinema_id = cgr_cinema_details.cinemaProviderPivot.idAtProvider
        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)

        films = cgr.get_films()

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12

        assert len(films) == 1
        assert films[0].IDFilm == 138473


@pytest.mark.usefixtures("db_session")
class GetFilmShowtimesStocksTest:
    @pytest.mark.settings(CGR_API_USER="pass_user")
    @pytest.mark.parametrize("response_body,expected_output", [([fixtures.FILM_138473], {"177182": 99}), ([], {})])
    def test_should_return_film_stocks_by_showtime(self, response_body, expected_output, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post("http://example.com/web_service", text=fixtures.cgr_response_template(response_body))
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/web_service")
        cinema_id = cgr_cinema_details.cinemaProviderPivot.idAtProvider
        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)

        data = cgr.get_film_showtimes_stocks(138473)

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12

        assert data == expected_output


@pytest.mark.usefixtures("db_session")
class GetNumCineTest:
    @pytest.mark.settings(CGR_API_USER="pass_user")
    def test_should_return_num_cine(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "http://example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/web_service")
        cinema_id = cgr_cinema_details.cinemaProviderPivot.idAtProvider
        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)

        num_cine = cgr.get_num_cine()

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12

        assert num_cine == 999


@pytest.mark.usefixtures("db_session")
class BookTicketTest:
    def test_should_book_one_ticket(self, requests_mock, app):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=1, amount=5.5, stock=showtime_stock)
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
        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)
        tickets = cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12
        assert len(tickets) == 1
        assert tickets[0].barcode == "CINE999508637111"
        assert tickets[0].seat_number == "D8"
        assert post_adapter.call_count == 1
        assert "<pNBPlaces>1</pNBPlaces>" in post_adapter.last_request.text
        assert "<pEmail>beneficiary@example.com</pEmail>" in post_adapter.last_request.text
        assert "<pPUTTC>5.50</pPUTTC>" in post_adapter.last_request.text
        assert "<pIDSeances>177182</pIDSeances>" in post_adapter.last_request.text
        assert (
            f"<pDateLimiteAnnul>{booking.cancellationLimitDate.strftime('%Y-%m-%dT%H:%M:%S.%f')}</pDateLimiteAnnul>"
            in post_adapter.last_request.text
        )
        redis_external_bookings = app.redis_client.lrange("api:external_bookings:barcodes", 0, -1)
        assert len(redis_external_bookings) == 1
        external_booking_info = json.loads(redis_external_bookings[0])
        assert external_booking_info["barcode"] == "CINE999508637111"
        assert external_booking_info["venue_id"] == venue_id
        assert external_booking_info["timestamp"]

    def test_should_book_one_ticket_when_placement_is_disabled(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=1, amount=5.5, stock=showtime_stock)
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

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)
        tickets = cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12
        assert len(tickets) == 1
        assert tickets[0].barcode == "CINE999508637111"
        assert not tickets[0].seat_number
        assert post_adapter.call_count == 1
        assert "<pNBPlaces>1</pNBPlaces>" in post_adapter.last_request.text
        assert "<pEmail>beneficiary@example.com</pEmail>" in post_adapter.last_request.text
        assert "<pPUTTC>5.50</pPUTTC>" in post_adapter.last_request.text
        assert "<pIDSeances>177182</pIDSeances>" in post_adapter.last_request.text
        assert (
            f"<pDateLimiteAnnul>{booking.cancellationLimitDate.strftime('%Y-%m-%dT%H:%M:%S.%f')}</pDateLimiteAnnul>"
            in post_adapter.last_request.text
        )

    def test_should_book_two_tickets(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2, amount=5.5, stock=showtime_stock)
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

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)
        tickets = cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12
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
        assert (
            f"<pDateLimiteAnnul>{booking.cancellationLimitDate.strftime('%Y-%m-%dT%H:%M:%S.%f')}</pDateLimiteAnnul>"
            in post_adapter.last_request.text
        )

    def test_should_book_two_tickets_when_placement_is_disabled(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2, amount=5.5, stock=showtime_stock)
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

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)
        tickets = cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12
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
        assert (
            f"<pDateLimiteAnnul>{booking.cancellationLimitDate.strftime('%Y-%m-%dT%H:%M:%S.%f')}</pDateLimiteAnnul>"
            in post_adapter.last_request.text
        )

    @pytest.mark.parametrize(
        "error_message,expected_remaining_quantity",
        [
            ("Impossible de délivrer 2 places , il n'en reste que : 0", 0),
            ("Impossible de délivrer 2 places , il n'en reste que : 1", 1),
            ("Impossible de délivrer 1 places , il n'en reste que : 0", 0),
        ],
    )
    def test_should_raise_not_enough_seat_exception(self, error_message, expected_remaining_quantity, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2, amount=5.5, stock=showtime_stock)
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://cgr-cinema-0.example.com/web_service"
        )
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.get(
            "http://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )

        requests_mock.post(
            "http://cgr-cinema-0.example.com/web_service",
            text=fixtures.cgr_reservation_error_response_template(
                99,  # not sure this is the actual error code for this error
                error_message,
            ),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)

        with pytest.raises(ExternalBookingNotEnoughSeatsError) as exc:
            cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)

        assert exc.value.remainingQuantity == expected_remaining_quantity

    @pytest.mark.parametrize(
        "error_message",
        [
            "Séance inconnue.",
            "PASS CULTURE IMPOSSIBLE erreur création résa (site) : IdSeance(528581) inconnu",
        ],
    )
    def test_should_raise_show_does_not_exist(self, error_message, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2, amount=5.5, stock=showtime_stock)
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://cgr-cinema-0.example.com/web_service"
        )
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.get(
            "http://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )

        requests_mock.post(
            "http://cgr-cinema-0.example.com/web_service",
            text=fixtures.cgr_reservation_error_response_template(
                99,  # not sure this is the actual error code for this error
                error_message,
            ),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id, request_timeout=12)

        with pytest.raises(ExternalBookingShowDoesNotExistError):
            cgr.book_ticket(show_id=177182, booking=booking, beneficiary=beneficiary)


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

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_str_id, request_timeout=12)

        cgr.cancel_booking(barcodes=["CINE-123456789"])

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12
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

    def test_when_cgr_returns_element_already_cancelled_on_cgr_side(self, requests_mock):
        cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="https://cinema-0.example.com/web_service"
        )
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get("https://cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "https://cinema-0.example.com/web_service",
            text=fixtures.cgr_annulation_response_template(
                message_error="Annulation impossible : La réservation a déjà fait l'objet d'une annulation",
                error_code=1,
            ),
        )

        cgr = cgr_client.CGRClientAPI(cinema_id=cinema_id)

        # should not raise
        cgr.cancel_booking(barcodes=["CINE-987654321"])
