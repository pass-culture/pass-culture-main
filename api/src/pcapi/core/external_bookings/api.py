from pcapi import settings
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository


def get_shows_stock(venue_id: int, shows_id: list[int]) -> dict[int, int]:
    client = _get_external_bookings_client_api(venue_id)
    return client.get_shows_remaining_places(shows_id)


def cancel_booking(venue_id: int, barcodes: list[str]) -> None:
    client = _get_external_bookings_client_api(venue_id)
    client.cancel_booking(barcodes)


def book_ticket(venue_id: int, show_id: int, quantity: int) -> list[external_bookings_models.Ticket]:
    client = _get_external_bookings_client_api(venue_id)
    return client.book_ticket(show_id, quantity)


def _get_external_bookings_client_api(venue_id: int) -> external_bookings_models.ExternalBookingsClientAPI:
    cinema_venue_provider = get_cinema_venue_provider(venue_id)
    cinema_id = cinema_venue_provider.venueIdAtOfferProvider
    match cinema_venue_provider.provider.localClass:
        case "CDSStocks":
            api_url = settings.CDS_API_URL
            cds_cinema_details = providers_repository.get_cds_cinema_details(cinema_id)
            cinema_api_token = cds_cinema_details.cinemaApiToken
            account_id = cds_cinema_details.accountId
            return CineDigitalServiceAPI(cinema_id, account_id, api_url, cinema_api_token)
        case "BoostStocks":
            boost_cinema_details = providers_repository.get_boost_cinema_details(cinema_id)
            cinema_str_id = boost_cinema_details.accountId
            return BoostClientAPI(cinema_str_id)
        case _:
            raise Exception(f"Unknown Provider: {cinema_venue_provider.provider.localClass}")


def get_cinema_venue_provider(venue_id: int) -> providers_models.VenueProvider:
    cinema_venue_provider = providers_repository.get_cinema_venue_provider_query(venue_id).one_or_none()

    if not cinema_venue_provider:
        raise Exception(f"No active cinema venue provider found for venue #{venue_id}")
    return cinema_venue_provider
