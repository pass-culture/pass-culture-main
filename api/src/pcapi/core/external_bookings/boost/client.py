import typing

from pydantic import parse_obj_as

from pcapi.connectors import boost
from pcapi.connectors.serialization import boost_serializers
import pcapi.core.external_bookings.models as external_bookings_models


class BoostClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    def __init__(self, cinema_str_id: str):
        self.cinema_str_id = cinema_str_id

    # FIXME: define those later
    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        pass

    def cancel_booking(self, barcodes: list[str]) -> None:
        pass

    def book_ticket(self, show_id: int, quantity: int) -> list[external_bookings_models.Ticket]:
        pass

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
