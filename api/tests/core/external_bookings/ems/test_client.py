import hmac
import json
from urllib.parse import urljoin

import pytest

from pcapi import settings
from pcapi.connectors.ems import EMSAPIException
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.external_bookings.ems.client import EMSClientAPI
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class EMSBookTicketTest:
    def _build_url(self, endpoint: str, payload: dict) -> str:
        base_url = urljoin(settings.EMS_API_BOOKING_URL, endpoint)
        h = hmac.new(settings.EMS_API_BOOKING_SECRET_KEY.encode(), digestmod="sha512")
        h.update(json.dumps(payload).encode())
        digest = h.hexdigest()

        return urljoin(base_url, digest)

    def test_we_can_book_one_ticket(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=1, amount=7.15, stock=showtime_stock)
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

        client = EMSClientAPI(cinema_id=cinema_id)
        ticket = client.book_ticket(show_id="999700079979", booking=booking, beneficiary=beneficiary)

        assert len(ticket) == 1
        ticket = ticket.pop()
        assert ticket.barcode == "000000144659"
        assert ticket.seat_number == ""

    def test_we_can_book_two_tickets_at_once(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2, amount=7.15, stock=showtime_stock)
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

        client = EMSClientAPI(cinema_id=cinema_id)
        tickets = client.book_ticket(show_id="999700079979", booking=booking, beneficiary=beneficiary)

        assert len(tickets) == 2
        assert tickets[0].barcode == "000000144659"
        assert tickets[0].seat_number == ""
        assert tickets[1].barcode == "000000144660"
        assert tickets[1].seat_number == ""

    def test_we_handle_no_session_left_case(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
        showtime_stock = offers_factories.EventStockFactory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=1, amount=7.15, stock=showtime_stock)
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
        }
        url = self._build_url("VENTE/", payload_reservation)

        #  TODO S’assurer que ce mock est conforme au retour API d’EMS, je n’ai pas réussi à "épuiser" de séances sur leur API de test
        expected_data = {
            "statut": 0,
            "code_erreur": 104,
            "message_erreur": "Il n'y a plus de séance disponible pour ce film",
        }

        requests_mock.post(url, json=expected_data, headers={"Source": settings.EMS_API_BOOKING_HEADER})

        client = EMSClientAPI(cinema_id=cinema_id)

        with pytest.raises(EMSAPIException):
            client.book_ticket(show_id="999700079979", booking=booking, beneficiary=beneficiary)
