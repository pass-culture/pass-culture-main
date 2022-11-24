import pytest

from pcapi.connectors.serialization import boost_serializers
from pcapi.core.external_bookings.boost.client import BoostClientAPI
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.providers.factories as providers_factories

from tests.local_providers.cinema_providers.boost import fixtures


pytestmark = pytest.mark.usefixtures("db_session")


class GetVenueMoviesTest:
    def test_should_return_movies_information(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get(
            "https://cinema-0.example.com/api/films?page=1&per_page=2",
            json=fixtures.FilmsEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/films?page=2&per_page=2",
            json=fixtures.FilmsEndpointResponse.PAGE_2_JSON_DATA,
        )
        boost = BoostClientAPI(cinema_str_id)
        movies = boost.get_venue_movies(per_page=2)

        assert movies == [
            external_bookings_models.Movie(
                id="207",
                title="BLACK PANTHER : WAKANDA FOREVER",
                duration=1,
                description="",
                posterpath="http://example.com/images/158026.jpg",
                visa="158026",
            ),
            external_bookings_models.Movie(
                id="210",
                title="CHARLOTTE",
                duration=1,
                description="",
                posterpath="http://example.com/images/149489.jpg",
                visa="149489",
            ),
            external_bookings_models.Movie(
                id="147",
                title="CASSE NOISETTE ROH 2021",
                duration=1,
                description="",
                posterpath="http://example.com/images/2021001414.jpg",
                visa="2021001414",
            ),
        ]


class GetShowtimesTest:
    def test_should_return_showtimes(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=2",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=2&per_page=2",
            json=fixtures.ShowtimesEndpointResponse.PAGE_2_JSON_DATA,
        )
        boost = BoostClientAPI(cinema_str_id)
        showtimes = boost.get_showtimes(per_page=2)
        assert showtimes == [
            boost_serializers.ShowTime3(id=36683),
            boost_serializers.ShowTime3(id=36848),
            boost_serializers.ShowTime3(id=36932),
        ]


class GetShowtimeRemainingSeatsTest:
    def test_number_of_remaining_seats_for_showtime(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/35278",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36683_DATA,
        )
        boost = BoostClientAPI(cinema_str_id)

        nb_remaining_online_seats = boost.get_showtime_remaining_online_seats(35278)

        assert nb_remaining_online_seats == 96


class BookTicketTest:
    def test_should_book_duo_tickets(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36683_DATA,
        )
        requests_mock.post(
            "https://cinema-0.example.com/api/sale/complete",
            json=fixtures.ConfirmedSaleEndpointResponse.DATA,
            headers={"Content-Type": "application/json"},
        )

        boost = BoostClientAPI(cinema_str_id)
        tickets = boost.book_ticket(show_id=36683, quantity=2)

        assert len(tickets) == 2
        assert tickets == [
            external_bookings_models.Ticket(barcode="PCU-000001-7174057", seat_number=None),
            external_bookings_models.Ticket(barcode="PCU-000002-7174058", seat_number=None),
        ]
