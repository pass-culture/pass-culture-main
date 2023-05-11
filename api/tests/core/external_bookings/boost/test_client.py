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
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/between/2022-10-10/2022-10-20?page=1&per_page=2",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/between/2022-10-10/2022-10-20?page=2&per_page=2",
            json=fixtures.ShowtimesEndpointResponse.PAGE_2_JSON_DATA,
        )
        boost = boost_client.BoostClientAPI(cinema_str_id)
        showtimes = boost.get_showtimes(per_page=2, start_date=date.date(2022, 10, 10), interval_days=10)
        assert showtimes == [
            boost_serializers.ShowTime4(id=36683, numberSeatsRemaining=96),
            boost_serializers.ShowTime4(id=36848, numberSeatsRemaining=177),
            boost_serializers.ShowTime4(id=36932, numberSeatsRemaining=122),
        ]

    def test_should_return_a_movie_showtimes(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/between/2022-10-10/2022-10-20?film=207&page=1&per_page=2",
            json=fixtures.ShowtimesWithFilmIdEndpointResponse.PAGE_1_JSON_DATA,
        )
        boost = boost_client.BoostClientAPI(cinema_str_id)
        showtimes = boost.get_showtimes(per_page=2, start_date=date.date(2022, 10, 10), interval_days=10, film=207)

        assert showtimes == [
            boost_serializers.ShowTime4(id=36683, numberSeatsRemaining=96),
            boost_serializers.ShowTime4(id=36684, numberSeatsRemaining=0),
        ]


class BookTicketTest:
    def test_should_book_duo_tickets(self, requests_mock, app):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2)
        venue_id = booking.venueId
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36684",
            json=fixtures.ShowtimeDetailsEndpointResponse.PC2_AND_FULL_PRICINGS_SHOWTIME_36684_DATA,
        )
        post_adapter = requests_mock.post(
            "https://cinema-0.example.com/api/sale/complete",
            json=fixtures.ConfirmedSaleEndpointResponse.DATA,
            headers={"Content-Type": "application/json"},
        )

        boost = boost_client.BoostClientAPI(cinema_str_id)
        tickets = boost.book_ticket(show_id=36684, booking=booking, beneficiary=beneficiary)

        showtime_info = boost.get_showtime(showtime_id=36684)
        assert showtime_info.showtimePricing == [FULL_PRICING, PC2_PRICING]
        assert post_adapter.last_request.json() == {
            "basketItems": [{"idShowtimePricing": 1114163, "quantity": 2}],
            "codePayment": "PCU",
        }
        assert len(tickets) == 2
        assert tickets == [
            external_bookings_models.Ticket(barcode="90474", seat_number=None),
            external_bookings_models.Ticket(barcode="90474", seat_number=None),
        ]
        redis_external_bookings = app.redis_client.lrange("api:external_bookings:barcodes", 0, -1)
        assert len(redis_external_bookings) == 1
        external_bookings_infos = json.loads(redis_external_bookings[0])
        assert external_bookings_infos["barcode"] == "90474"
        assert external_bookings_infos["venue_id"] == venue_id
        assert external_bookings_infos["timestamp"]


class CancelBookingTest:
    def test_should_cancel_booking_with_success(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.put(
            "https://cinema-0.example.com/api/sale/orderCancel",
            json=fixtures.CANCEL_ORDER_SALE_90577,
            headers={"Content-Type": "application/json"},
        )
        boost = boost_client.BoostClientAPI(cinema_str_id)

        try:
            boost.cancel_booking(barcodes=["90577"])
        except Exception:  # pylint: disable=broad-except
            assert False, "Should not raise exception"

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
