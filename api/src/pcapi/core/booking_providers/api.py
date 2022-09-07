import sqlalchemy.orm as sqla_orm

from pcapi.core.booking_providers.cds.client import CineDigitalServiceAPI
import pcapi.core.booking_providers.models as booking_providers_models
from pcapi.core.providers.repository import get_cds_cinema_details


def get_show_stock(venue_id: int, show_id: int) -> int:
    client = _get_booking_provider_client_api(venue_id)
    return client.get_show_remaining_places(show_id)


def get_shows_stock(venue_id: int, shows_id: list[int]) -> dict[int, int]:
    client = _get_booking_provider_client_api(venue_id)
    return client.get_shows_remaining_places(shows_id)


def get_available_seats(venue_id: int, show_id: int) -> booking_providers_models.SeatMap:
    client = _get_booking_provider_client_api(venue_id)
    return client.get_seatmap(show_id)


def cancel_booking(venue_id: int, barcodes: list[str]) -> None:
    client = _get_booking_provider_client_api(venue_id)
    client.cancel_booking(barcodes)


def book_ticket(venue_id: int, show_id: int, quantity: int) -> list[booking_providers_models.Ticket]:
    client = _get_booking_provider_client_api(venue_id)
    return client.book_ticket(show_id, quantity)


def get_venue_movies(venue_id: int) -> list[booking_providers_models.Movie]:
    client = _get_booking_provider_client_api(venue_id)
    return client.get_venue_movies()


def _get_booking_provider_client_api(venue_id: int) -> booking_providers_models.BookingProviderClientAPI:
    venue_booking_provider = _get_venue_booking_provider(venue_id)
    cinema_id = venue_booking_provider.idAtProvider
    api_url = venue_booking_provider.bookingProvider.apiUrl
    if venue_booking_provider.bookingProvider.name == booking_providers_models.BookingProviderName.CINE_DIGITAL_SERVICE:
        cds_cinema_details = get_cds_cinema_details(cinema_id)
        cinema_api_token = cds_cinema_details.cinemaApiToken
        account_id = cds_cinema_details.accountId
        return CineDigitalServiceAPI(cinema_id, account_id, api_url, cinema_api_token)
    raise Exception(f"No booking provider named : {venue_booking_provider.bookingProvider.name}")


def _get_venue_booking_provider(venue_id: int) -> booking_providers_models.VenueBookingProvider:
    venue_booking_provider = (
        booking_providers_models.VenueBookingProvider.query.filter(
            booking_providers_models.VenueBookingProvider.venueId == venue_id,
            booking_providers_models.VenueBookingProvider.isActive,
        )
        .options(sqla_orm.joinedload(booking_providers_models.VenueBookingProvider.bookingProvider, innerjoin=True))
        .one_or_none()
    )
    if not venue_booking_provider:
        raise Exception(f"No active booking provider found for venue #{venue_id}")
    return venue_booking_provider
