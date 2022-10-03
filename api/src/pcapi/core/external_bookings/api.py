from pcapi import settings
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.providers.models as providers_models
from pcapi.core.providers.repository import get_cds_cinema_details


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
    # FIXME (yacine-hc, 2022-10-06): edit this function when new cinema providers are implemented
    cinema_venue_provider = get_cinema_venue_provider(venue_id)
    cinema_id = cinema_venue_provider.venueIdAtOfferProvider
    api_url = settings.CDS_API_URL
    cds_cinema_details = get_cds_cinema_details(cinema_id)
    cinema_api_token = cds_cinema_details.cinemaApiToken
    account_id = cds_cinema_details.accountId
    return CineDigitalServiceAPI(cinema_id, account_id, api_url, cinema_api_token)


def get_cinema_venue_provider(venue_id: int) -> providers_models.VenueProvider:
    cinema_venue_provider = providers_models.VenueProvider.query.filter(
        providers_models.VenueProvider.venueId == venue_id,
        providers_models.VenueProvider.isFromCinemaProvider,
        providers_models.VenueProvider.isActive,
    ).one_or_none()

    if not cinema_venue_provider:
        raise Exception(f"No active cinema venue provider found for venue #{venue_id}")
    return cinema_venue_provider
