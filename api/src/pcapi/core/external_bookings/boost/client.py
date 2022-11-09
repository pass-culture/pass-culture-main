import typing

from pydantic import parse_obj_as

from pcapi.connectors import boost
from pcapi.connectors.serialization import boost_serializers
import pcapi.core.external_bookings.models as external_bookings_models

from . import constants
from . import exceptions


def get_pcu_pricing_if_exists(
    showtime_pricing_list: list[boost_serializers.ShowtimePricing],
) -> boost_serializers.ShowtimePricing | None:
    return next(
        (
            pricing
            for pricing in showtime_pricing_list
            if pricing.pricingCode == constants.BOOST_PASS_CULTURE_PRICING_CODE
        ),
        None,
    )


class BoostClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    def __init__(self, cinema_str_id: str):
        self.cinema_str_id = cinema_str_id

    # FIXME: define those later
    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:  # type: ignore [empty-body]
        pass

    def cancel_booking(self, barcodes: list[str]) -> None:
        pass

    def book_ticket(self, show_id: int, quantity: int) -> list[external_bookings_models.Ticket]:
        showtime = self.get_showtime(show_id)
        pcu_pricing = get_pcu_pricing_if_exists(showtime.showtimePricing)
        if not pcu_pricing:
            raise exceptions.BoostAPIException("No Pass Culture pricing was found")

        basket_items = [boost_serializers.BasketItem(idShowtimePricing=pcu_pricing.id, quantity=quantity)]
        sale_body = boost_serializers.SaleRequest(
            codePayment=pcu_pricing.pricingCode,
            basketItems=basket_items,
        )
        sale_response = boost.post_resource(self.cinema_str_id, boost.ResourceBoost.COMPLETE_SALE, sale_body)
        sale_confirmation_response = parse_obj_as(boost_serializers.SaleConfirmationResponse, sale_response)

        # FIXME(fseguin, 2022-11-08: waiting for the seat specs)
        tickets = []
        for ticket_response in sale_confirmation_response.data.tickets:
            seat_number = str(ticket_response.seat.id) if ticket_response.seat else None
            tickets.append(
                external_bookings_models.Ticket(barcode=ticket_response.ticketReference, seat_number=seat_number)
            )
        return tickets

    def get_collection_items(
        self,
        resource: boost.ResourceBoost,
        collection_class: typing.Type[boost_serializers.Collection],
        per_page: int = 30,
    ) -> list:
        # XXX: per_page max value seems to be 200
        items = []
        current_page = next_page = 1

        while current_page <= next_page:
            params = {"page": current_page, "per_page": per_page}
            json_data = boost.get_resource(self.cinema_str_id, resource, params=params)
            collection = parse_obj_as(collection_class, json_data)
            items.extend(collection.data)
            total_pages = collection.totalPages
            next_page = collection.nextPage
            current_page += 1
            if total_pages < current_page:
                break

        return items

    def get_venue_movies(self, per_page: int = 30) -> list[external_bookings_models.Movie]:
        films = self.get_collection_items(
            resource=boost.ResourceBoost.FILMS,
            collection_class=boost_serializers.FilmCollection,
            per_page=per_page,
        )
        return [film.to_generic_movie() for film in films]

    def get_showtimes(self, per_page: int = 30) -> list[boost_serializers.ShowTime3]:
        return self.get_collection_items(
            resource=boost.ResourceBoost.SHOWTIMES,
            collection_class=boost_serializers.ShowTimeCollection,
            per_page=per_page,
        )

    def get_showtime_remaining_online_seats(self, showtime_id: int) -> int:
        json_data = boost.get_resource(
            self.cinema_str_id,
            boost.ResourceBoost.SHOWTIME,
            pattern_values={"id": showtime_id},
        )
        res = parse_obj_as(boost_serializers.ShowTimeDetails, json_data)
        return res.data.numberRemainingSeatsForOnlineSale

    def get_showtime(self, showtime_id: int) -> boost_serializers.ShowTime:
        json_data = boost.get_resource(
            self.cinema_str_id,
            boost.ResourceBoost.SHOWTIME,
            params={"filter_payment_method": "external:credit:passculture"},
            pattern_values={"id": showtime_id},
        )
        showtime_details = parse_obj_as(boost_serializers.ShowTimeDetails, json_data)
        return showtime_details.data
