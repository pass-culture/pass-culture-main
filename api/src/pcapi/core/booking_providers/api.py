import sqlalchemy.orm as sqla_orm

from pcapi.core.booking_providers.cds.client import CineDigitalServiceAPI
from pcapi.core.booking_providers.models import BookingProviderClientAPI
from pcapi.core.booking_providers.models import BookingProviderName
from pcapi.core.booking_providers.models import VenueBookingProvider


def get_show_stock(venue_id: int, show_id: int) -> int:
    client = _get_booking_provider_client_api(venue_id)
    return client.get_show_remaining_places(show_id)


def get_available_seats(venue_id: int, show_id: int) -> list[list[int]]:
    client = _get_booking_provider_client_api(venue_id)
    return client.get_seatmap(show_id)


def cancel_booking(venue_id: int, barcodes: list[str]) -> None:
    client = _get_booking_provider_client_api(venue_id)
    client.cancel_booking(barcodes)


def _get_booking_provider_client_api(venue_id: int) -> BookingProviderClientAPI:
    venue_booking_provider = _get_venue_booking_provider(venue_id)
    cinema_id = venue_booking_provider.idAtProvider
    token = venue_booking_provider.token
    api_url = venue_booking_provider.bookingProvider.apiUrl
    if venue_booking_provider.bookingProvider.name == BookingProviderName.CINE_DIGITAL_SERVICE:
        if not token:
            raise Exception(f"No token found for {BookingProviderName.CINE_DIGITAL_SERVICE} provider")
        return CineDigitalServiceAPI(cinema_id, api_url, str(token))
    raise Exception(f"No booking provider named : {venue_booking_provider.bookingProvider.name}")


def _get_venue_booking_provider(venue_id: int) -> VenueBookingProvider:
    venue_booking_provider = venue_booking_provider = (
        VenueBookingProvider.query.options(sqla_orm.joinedload(VenueBookingProvider.bookingProvider, innerjoin=True))
        .filter(VenueBookingProvider.venueId == venue_id, VenueBookingProvider.isActive)
        .one_or_none()
    )
    if not venue_booking_provider:
        raise Exception(f"No active booking provider found for venue #{venue_id}")
    return venue_booking_provider
