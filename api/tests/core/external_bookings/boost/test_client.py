import datetime
from decimal import Decimal
import json

import pytest

from pcapi.connectors.serialization import boost_serializers
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.external_bookings.boost import client as boost_client
import pcapi.core.external_bookings.boost.exceptions as boost_exceptions
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils import date

from tests.local_providers.cinema_providers.boost import fixtures


pytestmark = pytest.mark.usefixtures("db_session")

FULL_PRICING = boost_serializers.ShowtimePricing(
    id=1225351, pricingCode="PLE", amountTaxesIncluded=Decimal(12), title="PLEIN TARIF"
)
PCU_PRICING = boost_serializers.ShowtimePricing(
    id=1117628, pricingCode="PCU", amountTaxesIncluded=Decimal(5.5), title="PASS CULTURE"
)
PC2_PRICING = boost_serializers.ShowtimePricing(
    id=1114163, pricingCode="PC2", amountTaxesIncluded=Decimal(18), title="PASS CULTURE 1"
)
PC3_PRICING = boost_serializers.ShowtimePricing(
    id=4, pricingCode="PC3", amountTaxesIncluded=Decimal(8.5), title="PASS CULTURE 2"
)


class GetPcuPricingIfExistsTest:
    def test_no_valid_pricing(self):
        showtime_pricing_list = [FULL_PRICING]

        assert not boost_client.get_pcu_pricing_if_exists(showtime_pricing_list)

    def test_one_valid_pricing(self):
        showtime_pricing_list = [FULL_PRICING, PCU_PRICING]

        assert boost_client.get_pcu_pricing_if_exists(showtime_pricing_list) == PCU_PRICING

    def test_two_pass_culture_pricings(self, caplog):
        showtime_pricing_list = [FULL_PRICING, PC2_PRICING, PC3_PRICING]

        assert boost_client.get_pcu_pricing_if_exists(showtime_pricing_list) == PC2_PRICING
        assert caplog.records[0].message == "There are several pass Culture Pricings for this Showtime, we will use PC2"

    def test_three_pass_culture_pricings(self, caplog):
        showtime_pricing_list = [FULL_PRICING, PC2_PRICING, PC3_PRICING, PCU_PRICING]

        assert boost_client.get_pcu_pricing_if_exists(showtime_pricing_list) == PCU_PRICING
        assert caplog.records[0].message == "There are several pass Culture Pricings for this Showtime, we will use PCU"


class GetShowtimesTest:
    def test_should_return_showtimes(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        start_date = datetime.date.today()
        end_date = (start_date + datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{start_date.strftime('%Y-%m-%d')}/{end_date}?paymentMethod=external%3Acredit%3Apassculture&hideFullReservation=1&page=1&per_page=2",
            json=fixtures.ShowtimesWithPaymentMethodFilterEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{start_date.strftime('%Y-%m-%d')}/{end_date}?paymentMethod=external%3Acredit%3Apassculture&hideFullReservation=1&page=2&per_page=2",
            json=fixtures.ShowtimesWithPaymentMethodFilterEndpointResponse.PAGE_2_JSON_DATA,
        )
        boost = boost_client.BoostClientAPI(cinema_str_id)
        showtimes = boost.get_showtimes(per_page=2, start_date=start_date, interval_days=10)
        assert len(showtimes) == 3
        assert showtimes[0].id == 15971
        assert showtimes[0].numberSeatsRemaining == 147
        assert showtimes[0].film.titleCnc == "MISSION IMPOSSIBLE DEAD RECKONING PARTIE 1"
        assert showtimes[0].version == {"code": "VF", "id": 3, "title": "Film Etranger en Langue Française"}
        assert showtimes[0].screen
        assert showtimes[0].showtimePricing == [
            boost_serializers.ShowtimePricing(
                id=537105, pricingCode="PCU", amountTaxesIncluded=Decimal("12.0"), title="PASS CULTURE"
            )
        ]
        assert showtimes[0].attributs == [35, 44, 24, 1, 29, 40]
        assert showtimes[1].id == 16277
        assert showtimes[1].numberSeatsRemaining == 452
        assert showtimes[1].film.titleCnc == "SPIDER-MAN ACROSS THE SPIDER-VERSE"
        assert showtimes[1].version == {"code": "VO", "id": 2, "title": "Film Etranger en Langue Etrangère"}
        assert showtimes[1].screen
        assert showtimes[1].showtimePricing == [
            boost_serializers.ShowtimePricing(
                id=537354, pricingCode="PCU", amountTaxesIncluded=Decimal("6.0"), title="PASS CULTURE"
            )
        ]
        assert showtimes[1].attributs == [51, 45, 1, 40]
        assert showtimes[2].id == 15978
        assert showtimes[2].numberSeatsRemaining == 152
        assert showtimes[2].film.titleCnc == "SPIDER-MAN ACROSS THE SPIDER-VERSE"
        assert showtimes[2].version == {"code": "VF", "id": 3, "title": "Film Etranger en Langue Française"}
        assert showtimes[2].screen
        assert showtimes[2].showtimePricing == [
            boost_serializers.ShowtimePricing(
                id=537132, pricingCode="PCU", amountTaxesIncluded=Decimal("12.0"), title="PASS CULTURE"
            )
        ]
        assert showtimes[2].attributs == [24, 1, 29, 40]

    def test_should_return_a_movie_showtimes(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/between/2022-10-10/2022-10-20?film=207&paymentMethod=external:credit:passculture&hideFullReservation=1&page=1&per_page=2",
            json=fixtures.ShowtimesWithFilmIdAndPaymentMethodFilterEndpointResponse.PAGE_1_JSON_DATA,
        )
        boost = boost_client.BoostClientAPI(cinema_str_id)
        showtimes = boost.get_showtimes(per_page=2, start_date=date.date(2022, 10, 10), interval_days=10, film=207)

        assert len(showtimes) == 2
        assert showtimes[0].id == 16277
        assert showtimes[0].numberSeatsRemaining == 452
        assert showtimes[0].film.titleCnc == "SPIDER-MAN ACROSS THE SPIDER-VERSE"
        assert showtimes[0].version == {"code": "VO", "id": 2, "title": "Film Etranger en Langue Etrangère"}
        assert showtimes[0].screen
        assert showtimes[0].showtimePricing == [
            boost_serializers.ShowtimePricing(
                id=537354, pricingCode="PCU", amountTaxesIncluded=Decimal("6.0"), title="PASS CULTURE"
            )
        ]
        assert showtimes[0].attributs == [51, 45, 1, 40]
        assert showtimes[1].id == 15978
        assert showtimes[1].numberSeatsRemaining == 152
        assert showtimes[1].film.titleCnc == "SPIDER-MAN ACROSS THE SPIDER-VERSE"
        assert showtimes[1].version == {"code": "VF", "id": 3, "title": "Film Etranger en Langue Française"}
        assert showtimes[1].screen
        assert showtimes[1].showtimePricing == [
            boost_serializers.ShowtimePricing(
                id=537132, pricingCode="PCU", amountTaxesIncluded=Decimal("12.0"), title="PASS CULTURE"
            )
        ]
        assert showtimes[1].attributs == [24, 1, 29, 40]


class BookTicketTest:
    def test_should_book_duo_tickets(self, requests_mock, app):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2)
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36684",
            json=fixtures.ShowtimeDetailsEndpointResponse.PC2_AND_FULL_PRICINGS_SHOWTIME_36684_DATA,
        )
        pre_sale_post_adapter = requests_mock.post(
            "https://cinema-0.example.com/api/sale/complete",
            json=fixtures.CompleteSaleEndpointResponse.PRE_SALE_CONFIRMATION,
            headers={"Content-Type": "application/json"},
            additional_matcher=lambda request: not request.json().get("idsBeforeSale"),
        )
        confirmation_sale_post_adapter = requests_mock.post(
            "https://cinema-0.example.com/api/sale/complete",
            json=fixtures.CompleteSaleEndpointResponse.SALE_CONFIRMATION,
            headers={"Content-Type": "application/json"},
            additional_matcher=lambda request: bool(request.json().get("idsBeforeSale")),
        )
        boost = boost_client.BoostClientAPI(cinema_str_id)
        tickets = boost.book_ticket(show_id=36684, booking=booking, beneficiary=beneficiary)
        assert pre_sale_post_adapter.last_request.json() == {
            "basketItems": [{"idShowtimePricing": 1114163, "quantity": 2}],
            "codePayment": "PCU",
            "idsBeforeSale": None,
        }
        assert confirmation_sale_post_adapter.last_request.json() == {
            "basketItems": [
                {
                    "idShowtimePricing": 1114163,
                    "quantity": 2,
                },
            ],
            "codePayment": "PCU",
            "idsBeforeSale": "3",
        }
        assert len(tickets) == 2
        assert tickets == [
            external_bookings_models.Ticket(barcode="sale-133401", seat_number=None),
            external_bookings_models.Ticket(barcode="sale-133401", seat_number=None),
        ]
        redis_external_bookings = app.redis_client.lrange("api:external_bookings:barcodes", 0, -1)
        assert len(redis_external_bookings) == 1
        external_bookings_infos = json.loads(redis_external_bookings[0])
        assert external_bookings_infos["barcode"] == "sale-133401"
        assert external_bookings_infos["timestamp"]
        assert external_bookings_infos["venue_id"] == booking.venueId


class CancelBookingTest:

    def test_should_cancel_booking_with_success(self, requests_mock):
        barcode = "sale-90577"
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        put_adapter = requests_mock.put(
            "https://cinema-0.example.com/api/sale/orderCancel",
            json=fixtures.CANCEL_ORDER_SALE_90577,
            headers={"Content-Type": "application/json"},
        )
        boost = boost_client.BoostClientAPI(cinema_str_id)

        try:
            boost.cancel_booking(barcodes=[barcode])
        except Exception:  # pylint: disable=broad-except
            assert False, "Should not raise exception"
        assert put_adapter.last_request.json() == {"sales": [{"code": barcode, "refundType": "pcu"}]}

    def test_when_boost_return_element_not_found(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.put(
            "https://cinema-0.example.com/api/sale/orderCancel",
            headers={"Content-Type": "application/json"},
            json={"code": 404, "message": "The sale with ID: 55555 not found"},
            reason="Not found",
            status_code=404,
        )
        boost = boost_client.BoostClientAPI(cinema_str_id)

        with pytest.raises(boost_exceptions.BoostAPIException) as exception:
            boost.cancel_booking(barcodes=["55555"])

        assert (
            str(exception.value)
            == "Error on Boost API on PUT ResourceBoost.CANCEL_ORDER_SALE : Not found - The sale with ID: 55555 not found"
        )
