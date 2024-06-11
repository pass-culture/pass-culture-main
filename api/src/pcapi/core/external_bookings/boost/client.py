import datetime
import json
import logging
import typing

from pydantic.v1 import parse_obj_as

from pcapi.connectors import boost
from pcapi.connectors.serialization import boost_serializers
import pcapi.core.bookings.constants as bookings_constants
import pcapi.core.bookings.models as bookings_models
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.users.models as users_models
from pcapi.models.feature import FeatureToggle
from pcapi.utils.queue import add_to_queue

from . import constants
from . import exceptions


logger = logging.getLogger(__name__)


def get_pcu_pricing_if_exists(
    showtime_pricing_list: list[boost_serializers.ShowtimePricing],
) -> boost_serializers.ShowtimePricing | None:
    pcu_pricings = [
        pricing
        for pricing in showtime_pricing_list
        if pricing.pricingCode in constants.BOOST_PASS_CULTURE_PRICING_CODES
    ]
    if len(pcu_pricings) == 0:
        return None

    pcu_pricings_sorted_by_code = sorted(
        pcu_pricings, key=lambda p: constants.BOOST_PASS_CULTURE_PRICING_CODES.index(p.pricingCode)
    )
    first_pcu_pricing = pcu_pricings_sorted_by_code[0]

    if len(pcu_pricings) > 1:
        logger.warning(
            "There are several pass Culture Pricings for this Showtime, we will use %s", first_pcu_pricing.pricingCode
        )

    return first_pcu_pricing


class BoostClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    # FIXME: define those later
    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[str, int]:
        raise NotImplementedError()

    @external_bookings_models.cache_external_call(
        key_template=constants.BOOST_SHOWTIMES_STOCKS_CACHE_KEY, expire=constants.BOOST_SHOWTIMES_STOCKS_CACHE_TIMEOUT
    )
    def get_film_showtimes_stocks(self, film_id: str) -> str:
        showtimes = self.get_showtimes(film=int(film_id))
        return json.dumps({showtime.id: showtime.numberSeatsRemaining for showtime in showtimes})

    def cancel_booking(self, barcodes: list[str]) -> None:
        barcodes = list(set(barcodes))
        sale_cancel_items = []
        for barcode in barcodes:
            sale_cancel_item = boost_serializers.SaleCancelItem(
                code=barcode, refundType=constants.BOOST_PASS_CULTURE_REFUND_TYPE
            )
            sale_cancel_items.append(sale_cancel_item)

        sale_cancel = boost_serializers.SaleCancel(sales=sale_cancel_items)
        boost.put_resource(self.cinema_id, boost.ResourceBoost.CANCEL_ORDER_SALE, sale_cancel)

    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[external_bookings_models.Ticket]:
        quantity = booking.quantity
        showtime = self.get_showtime(show_id)
        pcu_pricing = get_pcu_pricing_if_exists(showtime.showtimePricing)
        if not pcu_pricing:
            raise exceptions.BoostAPIException(f"pass Culture pricing not found for show {show_id}")

        basket_items = [boost_serializers.BasketItem(idShowtimePricing=pcu_pricing.id, quantity=quantity)]
        sale_body = boost_serializers.SaleRequest(
            codePayment=constants.BOOST_PASS_CULTURE_CODE_PAYMENT, basketItems=basket_items, idsBeforeSale=None
        )
        sale_preparation_response = boost.post_resource(self.cinema_id, boost.ResourceBoost.COMPLETE_SALE, sale_body)
        sale_preparation = parse_obj_as(boost_serializers.SalePreparationResponse, sale_preparation_response)

        sale_body.idsBeforeSale = str(sale_preparation.data[0].id)
        sale_response = boost.post_resource(self.cinema_id, boost.ResourceBoost.COMPLETE_SALE, sale_body)
        sale_confirmation_response = parse_obj_as(boost_serializers.SaleConfirmationResponse, sale_response)
        add_to_queue(
            bookings_constants.REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": sale_confirmation_response.data.code,
                "venue_id": booking.venueId,
                "timestamp": datetime.datetime.utcnow().timestamp(),
                "booking_type": bookings_constants.RedisExternalBookingType.CINEMA,
            },
        )

        tickets = []
        for ticket_response in sale_confirmation_response.data.tickets:
            # same barcode for each Ticket of the sale
            barcode = sale_confirmation_response.data.code
            seat_number = str(ticket_response.seat.id) if ticket_response.seat else None
            extra_data = {
                "barcode": barcode,
                "seat_number": seat_number,
                "ticketReference": ticket_response.ticketReference,
                "total_amount": sale_confirmation_response.data.amountTaxesIncluded,
            }
            # This will be useful for customer support
            logger.info("Booked Boost Ticket", extra=extra_data)
            ticket = external_bookings_models.Ticket(barcode=barcode, seat_number=seat_number)
            tickets.append(ticket)

        return tickets

    def get_collection_items(
        self,
        resource: boost.ResourceBoost,
        collection_class: type[boost_serializers.Collection],
        per_page: int = 30,
        pattern_values: dict[str, typing.Any] | None = None,
        params: dict[str, typing.Any] | None = None,
    ) -> list:
        # XXX: per_page max value seems to be 200
        items = []
        current_page = next_page = 1

        while current_page <= next_page:
            if params:
                params["page"] = current_page
                params["per_page"] = per_page
            else:
                params = {"page": current_page, "per_page": per_page}
            json_data = boost.get_resource(self.cinema_id, resource, params=params, pattern_values=pattern_values)
            collection = parse_obj_as(collection_class, json_data)
            items.extend(collection.data)
            total_pages = collection.totalPages
            next_page = collection.nextPage
            current_page += 1
            if total_pages < current_page:
                break

        return items

    def get_showtimes(
        self,
        per_page: int = 30,
        start_date: datetime.date = datetime.date.today(),
        interval_days: int = constants.BOOST_SHOWS_INTERVAL_DAYS,
        film: int | None = None,
    ) -> list[boost_serializers.ShowTime4]:
        pattern_values = {
            "dateStart": start_date.strftime("%Y-%m-%d"),
            "dateEnd": (start_date + datetime.timedelta(days=interval_days)).strftime("%Y-%m-%d"),
        }
        params: dict[str, str | int | None] | None = None
        if FeatureToggle.WIP_ENABLE_BOOST_SHOWTIMES_FILTER.is_active():
            params = {
                "paymentMethod": constants.BOOST_PASS_CULTURE_PAYMENT_METHOD,
                "hideFullReservation": constants.BOOST_HIDE_FULL_RESERVATION,
                "film": film,
            }
        else:
            params = {"film": film} if film else None
        return self.get_collection_items(
            resource=boost.ResourceBoost.SHOWTIMES,
            collection_class=boost_serializers.ShowTimeCollection,
            per_page=per_page,
            pattern_values=pattern_values,
            params=params,
        )

    def get_showtime(self, showtime_id: int) -> boost_serializers.ShowTime4:
        json_data = boost.get_resource(
            self.cinema_id,
            boost.ResourceBoost.SHOWTIME,
            pattern_values={"id": showtime_id},
        )
        showtime_details = parse_obj_as(boost_serializers.ShowTimeDetails, json_data)
        return showtime_details.data

    def get_movie_poster(self, image_url: str) -> bytes:
        try:
            return boost.get_movie_poster_from_api(image_url)
        except exceptions.BoostAPIException:
            logger.info(
                "Could not fetch movie poster",
                extra={
                    "provider": "boost",
                    "url": image_url,
                },
            )
            return bytes()

    def get_cinemas_attributs(self) -> list[boost_serializers.CinemaAttribut]:
        json_data = boost.get_resource(
            self.cinema_id,
            boost.ResourceBoost.CINEMAS_ATTRIBUTS,
        )
        attributs = parse_obj_as(boost_serializers.CinemaAttributCollection, json_data)
        return attributs.data
