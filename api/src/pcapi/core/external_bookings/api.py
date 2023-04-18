from pcapi import settings
import pcapi.core.bookings.models as bookings_models
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
from pcapi.core.external_bookings.cgr.client import CGRClientAPI
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
import pcapi.core.users.models as users_models


def get_shows_stock(venue_id: int, shows_id: list[int]) -> dict[int, int]:
    client = _get_external_bookings_client_api(venue_id)
    return client.get_shows_remaining_places(shows_id)


def get_movie_stocks(venue_id: int, movie_id: int) -> dict[int, int]:
    client = _get_external_bookings_client_api(venue_id)
    return client.get_film_showtimes_stocks(movie_id)


def cancel_booking(venue_id: int, barcodes: list[str]) -> None:
    client = _get_external_bookings_client_api(venue_id)
    client.cancel_booking(barcodes)


def book_ticket(
    venue_id: int, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
) -> list[external_bookings_models.Ticket]:
    client = _get_external_bookings_client_api(venue_id)
    return client.book_ticket(show_id, booking, beneficiary)


def _get_external_bookings_client_api(venue_id: int) -> external_bookings_models.ExternalBookingsClientAPI:
    cinema_venue_provider = get_active_cinema_venue_provider(venue_id)
    cinema_id = cinema_venue_provider.venueIdAtOfferProvider
    match cinema_venue_provider.provider.localClass:
        case "CDSStocks":
            api_url = settings.CDS_API_URL
            cds_cinema_details = providers_repository.get_cds_cinema_details(cinema_id)
            cinema_api_token = cds_cinema_details.cinemaApiToken
            account_id = cds_cinema_details.accountId
            return CineDigitalServiceAPI(cinema_id, account_id, api_url, cinema_api_token)
        case "BoostStocks":
            return BoostClientAPI(cinema_id)
        case "CGRStocks":
            return CGRClientAPI(cinema_id)
        case _:
            raise ValueError(f"Unknown Provider: {cinema_venue_provider.provider.localClass}")


def get_active_cinema_venue_provider(venue_id: int) -> providers_models.VenueProvider:
    cinema_venue_provider = (
        providers_repository.get_cinema_venue_provider_query(venue_id)
        .filter(providers_models.VenueProvider.isActive)
        .one_or_none()
    )
    if not cinema_venue_provider:
        raise providers_exceptions.InactiveProvider(f"No active cinema venue provider found for venue #{venue_id}")
    return cinema_venue_provider
