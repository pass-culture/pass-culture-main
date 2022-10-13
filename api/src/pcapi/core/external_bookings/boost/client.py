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

    def get_venue_movies(self, per_page: int = 30) -> list[external_bookings_models.Movie]:
        # XXX: per_page max value seems to be 200
        venue_movies = []
        current_page = next_page = 1

        while current_page <= next_page:
            params = {"page": current_page, "per_page": per_page}
            json_data = boost.get_resource(self.cinema_str_id, boost.ResourceBoost.MEDIA, params=params)
            media_list_page: boost_serializers.FilmCollection = parse_obj_as(
                boost_serializers.FilmCollection, json_data
            )
            venue_movies.extend([movie.to_generic_movie() for movie in media_list_page.data])
            total_pages = media_list_page.totalPages
            next_page = media_list_page.nextPage
            current_page += 1
            if total_pages < current_page:
                break

        return venue_movies
