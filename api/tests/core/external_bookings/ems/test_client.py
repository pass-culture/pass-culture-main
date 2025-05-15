import hmac
import json
import re
from urllib.parse import urljoin

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi import settings
from pcapi.core.external_bookings.ems.client import EMSClientAPI
from pcapi.core.external_bookings.exceptions import ExternalBookingSoldOutError


@pytest.mark.usefixtures("db_session")
class EMSBookTicketTest:
    def _build_url(self, endpoint: str, payload: dict) -> str:
        base_url = urljoin(settings.EMS_API_BOOKING_URL, endpoint)
        h = hmac.new(settings.EMS_API_BOOKING_SECRET_KEY.encode(), digestmod="sha512")
        h.update(json.dumps(payload).encode())
        digest = h.hexdigest()

        return urljoin(base_url, digest)

    def test_we_can_book_one_ticket(self, requests_mock):
        token = "AAAAAA"
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(
            user=beneficiary, quantity=1, amount=7.15, stock=showtime_stock, token="AAAAAA"
        )
        cinema_pivot = providers_factories.EMSCinemaProviderPivotFactory(idAtProvider="9997")
        cinema_details = providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_pivot)
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        payload_reservation = {
            "num_cine": "9997",
            "id_seance": "999700079979",
            "qte_place": 1,
            "pass_culture_price": 7.15,
            "total_price": 7.15,
            "email": beneficiary.email,
            "num_pass_culture": str(beneficiary.id),
            "num_cmde": token,
        }
        url = self._build_url("VENTE/", payload_reservation)

        expected_data = {
            "statut": 1,
            "num_cine": "9997",
            "id_seance": "999700079979",
            "qte_place": 1,
            "pass_culture_price": 7.15,
            "total_price": 7.15,
            "email": beneficiary.email,
            "num_pass_culture": beneficiary.id,
            "num_cmde": token,
            "billets": [
                {
                    "num_caisse": "255",
                    "code_barre": "000000144659",
                    "num_trans": 534,
                    "num_ope": 144659,
                    "code_tarif": "0RH",
                    "num_serie": 2,
                    "montant": 7.15,
                    "num_place": "",
                }
            ],
        }

        requests_mock.post(url, json=expected_data, headers={"Source": settings.EMS_API_BOOKING_HEADER})

        client = EMSClientAPI(cinema_id=cinema_id, request_timeout=12)
        ticket = client.book_ticket(show_id="999700079979", booking=booking, beneficiary=beneficiary)

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12
        assert len(ticket) == 1
        ticket = ticket.pop()
        assert ticket.barcode == "000000144659"
        assert ticket.seat_number == ""

    def test_we_can_book_two_tickets_at_once(self, requests_mock):
        token = "AAAAAA"
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(
            user=beneficiary, quantity=2, amount=7.15, stock=showtime_stock, token=token
        )
        cinema_pivot = providers_factories.EMSCinemaProviderPivotFactory(idAtProvider="9997")
        cinema_details = providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_pivot)
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        payload_reservation = {
            "num_cine": "9997",
            "id_seance": "999700079979",
            "qte_place": 2,
            "pass_culture_price": 7.15,
            "total_price": 14.30,
            "email": beneficiary.email,
            "num_pass_culture": str(beneficiary.id),
            "num_cmde": token,
        }
        url = self._build_url("VENTE/", payload_reservation)

        expected_data = {
            "statut": 1,
            "num_cine": "9997",
            "id_seance": "999700079979",
            "qte_place": 2,
            "pass_culture_price": 14.30,
            "total_price": 14.30,
            "email": beneficiary.email,
            "num_pass_culture": beneficiary.id,
            "num_cmde": token,
            "billets": [
                {
                    "num_caisse": "255",
                    "code_barre": "000000144659",
                    "num_trans": 534,
                    "num_ope": 144659,
                    "code_tarif": "0RH",
                    "num_serie": 2,
                    "montant": 7.15,
                    "num_place": "",
                },
                {
                    "num_caisse": "255",
                    "code_barre": "000000144660",
                    "num_trans": 534,
                    "num_ope": 144660,
                    "code_tarif": "0RH",
                    "num_serie": 3,
                    "montant": 7.15,
                    "num_place": "",
                },
            ],
        }

        requests_mock.post(url, json=expected_data, headers={"Source": settings.EMS_API_BOOKING_HEADER})

        client = EMSClientAPI(cinema_id=cinema_id, request_timeout=12)
        tickets = client.book_ticket(show_id="999700079979", booking=booking, beneficiary=beneficiary)

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 12
        assert len(tickets) == 2
        assert tickets[0].barcode == "000000144659"
        assert tickets[0].seat_number == ""
        assert tickets[1].barcode == "000000144660"
        assert tickets[1].seat_number == ""

    def test_we_handle_no_session_left_case(self, requests_mock):
        token = "AAAAAA"
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(
            user=beneficiary, quantity=1, amount=7.15, stock=showtime_stock, token=token
        )
        cinema_pivot = providers_factories.EMSCinemaProviderPivotFactory(idAtProvider="9997")
        cinema_details = providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_pivot)
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        payload_reservation = {
            "num_cine": "9997",
            "id_seance": "999700079979",
            "qte_place": 1,
            "pass_culture_price": 7.15,
            "total_price": 7.15,
            "email": beneficiary.email,
            "num_pass_culture": str(beneficiary.id),
            "num_cmde": token,
        }
        url = self._build_url("VENTE/", payload_reservation)

        expected_data = {
            "statut": 0,
            "code_erreur": 104,
            "message_erreur": "Il n'y a plus de séance disponible pour ce film",
        }

        requests_mock.post(url, json=expected_data, headers={"Source": settings.EMS_API_BOOKING_HEADER})

        client = EMSClientAPI(cinema_id=cinema_id)

        with pytest.raises(ExternalBookingSoldOutError):
            client.book_ticket(show_id="999700079979", booking=booking, beneficiary=beneficiary)


@pytest.mark.usefixtures("db_session")
class EMSGetFilmShowtimesStocksTest:
    def test_get_film_showtimes_stocks(self, requests_mock):
        cinema_pivot = providers_factories.EMSCinemaProviderPivotFactory(idAtProvider="0003")
        cinema_details = providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_pivot)
        cinema_id = cinema_details.cinemaProviderPivot.idAtProvider

        response_json = {
            "statut": 1,
            "seances": [
                "999000111",
                "998880001",
            ],
        }

        url_matcher = re.compile("https://fake_url.com/SEANCE/*")
        requests_mock.post(url=url_matcher, json=response_json)

        client = EMSClientAPI(cinema_id=cinema_id, request_timeout=14)
        stocks = client.get_film_showtimes_stocks("12345")

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 14
        assert len(stocks) == 2
        assert stocks == {"999000111": 100, "998880001": 100}
