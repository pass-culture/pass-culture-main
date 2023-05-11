import datetime
import logging
import typing

from pydantic import parse_obj_as

from pcapi.connectors import boost
from pcapi.connectors.serialization import boost_serializers
import pcapi.core.bookings.constants as bookings_constants
import pcapi.core.bookings.models as bookings_models
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.users.models as users_models
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
    def __init__(self, cinema_str_id: str):
        self.cinema_str_id = cinema_str_id

    # FIXME: define those later
    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:  # type: ignore [empty-body]
        pass

    def get_film_showtimes_stocks(self, film_id: int) -> dict[int, int]:
        showtimes = self.get_showtimes(film=film_id)
        return {showtime.id: showtime.numberSeatsRemaining for showtime in showtimes}

    def cancel_booking(self, barcodes: list[str]) -> None:
        barcodes = list(set(barcodes))
        sale_cancel_items = []
        for barcode in barcodes:
            sale_cancel_item = boost_serializers.SaleCancelItem(
                code=constants.BOOST_SALE_PREFIX + barcode, refundType=constants.BOOST_PASS_CULTURE_REFUND_TYPE
            )
            sale_cancel_items.append(sale_cancel_item)

        sale_cancel = boost_serializers.SaleCancel(sales=sale_cancel_items)
        boost.put_resource(self.cinema_str_id, boost.ResourceBoost.CANCEL_ORDER_SALE, sale_cancel)

    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[external_bookings_models.Ticket]:
        quantity = booking.quantity
        showtime = self.get_showtime(show_id)
        pcu_pricing = get_pcu_pricing_if_exists(showtime.showtimePricing)
        if not pcu_pricing:
            raise exceptions.BoostAPIException("No Pass Culture pricing was found")

        basket_items = [boost_serializers.BasketItem(idShowtimePricing=pcu_pricing.id, quantity=quantity)]
        sale_body = boost_serializers.SaleRequest(
            codePayment=constants.BOOST_PASS_CULTURE_CODE_PAYMENT,
            basketItems=basket_items,
        )
        sale_response = boost.post_resource(self.cinema_str_id, boost.ResourceBoost.COMPLETE_SALE, sale_body)
        sale_confirmation_response = parse_obj_as(boost_serializers.SaleConfirmationResponse, sale_response)
        add_to_queue(
            bookings_constants.REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": str(sale_confirmation_response.data.id),
                "venue_id": booking.venueId,
                "timestamp": datetime.datetime.utcnow().timestamp(),
            },
        )

        tickets = []
        for ticket_response in sale_confirmation_response.data.tickets:
            # same barcode for each Ticket of the sale
            barcode = str(sale_confirmation_response.data.id)
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
        collection_class: typing.Type[boost_serializers.Collection],
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
            json_data = boost.get_resource(self.cinema_str_id, resource, params=params, pattern_values=pattern_values)
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
        return self.get_collection_items(
            resource=boost.ResourceBoost.SHOWTIMES,
            collection_class=boost_serializers.ShowTimeCollection,
            per_page=per_page,
            pattern_values=pattern_values,
            params={"film": film} if film else None,
        )

    def get_showtime(self, showtime_id: int) -> boost_serializers.ShowTime:
        json_data = boost.get_resource(
            self.cinema_str_id,
            boost.ResourceBoost.SHOWTIME,
            # TODO(fseguin, 2022-02-06): filter again when BB API is ready
            # params={"filter_payment_method": constants.BOOST_PASS_CULTURE_PAYMENT_METHOD},
            pattern_values={"id": showtime_id},
        )
        showtime_details = parse_obj_as(boost_serializers.ShowTimeDetails, json_data)
        return showtime_details.data

    def get_movie_poster(self, image_url: str) -> bytes:
        return boost.get_movie_poster_from_api(image_url)
