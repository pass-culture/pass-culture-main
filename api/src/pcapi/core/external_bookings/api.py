import datetime
import typing

import pydantic

from pcapi import settings
from pcapi.core.bookings.constants import REDIS_EXTERNAL_BOOKINGS_NAME
import pcapi.core.bookings.models as bookings_models
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
from pcapi.core.external_bookings.cgr.client import CGRClientAPI
from pcapi.core.external_bookings.ems.client import EMSClientAPI
import pcapi.core.external_bookings.models as external_bookings_models
from pcapi.core.external_bookings.models import Ticket
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
import pcapi.core.users.models as users_models
from pcapi.utils import requests
from pcapi.utils.queue import add_to_queue

from . import exceptions
from . import serialize


def get_shows_stock(venue_id: int, shows_id: list[int]) -> dict[int, int]:
    client = _get_external_bookings_client_api(venue_id)
    return client.get_shows_remaining_places(shows_id)


def get_movie_stocks(venue_id: int, movie_id: str) -> dict[int, int]:
    client = _get_external_bookings_client_api(venue_id)
    return client.get_film_showtimes_stocks(movie_id)


def cancel_booking(venue_id: int, barcodes: list[str]) -> None:
    client = _get_external_bookings_client_api(venue_id)
    client.cancel_booking(barcodes)


def book_cinema_ticket(
    venue_id: int, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
) -> list[external_bookings_models.Ticket]:
    client = _get_external_bookings_client_api(venue_id)
    return client.book_ticket(show_id, booking, beneficiary)


def cancel_event_ticket(
    provider: providers_models.Provider,
    stock: offers_models.Stock,
    barcodes: list[str],
) -> None:
    payload = serialize.ExternalEventCancelBookingRequest.build_external_cancel_booking(barcodes)
    headers = {"Content-Type": "application/json"}
    response = requests.post(provider.cancelExternalUrl, json=payload.json(), headers=headers)
    parsed_response = pydantic.parse_obj_as(serialize.ExternalEventCancelBookingResponse, response.json())
    if response.status_code != 200:
        if parsed_response.remainingQuantity:
            stock.quantity = parsed_response.remainingQuantity + stock.dnBookedQuantity
        raise exceptions.ExternalBookingException(
            f"External booking failed with status code {response.status_code} and message {response.text}"
        )
    stock.dnBookedQuantity -= len(barcodes)
    if parsed_response.remainingQuantity:
        stock.quantity = parsed_response.remainingQuantity + stock.dnBookedQuantity


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
        case "EMSStocks":
            return EMSClientAPI(cinema_id)
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


def book_event_ticket(
    booking: bookings_models.Booking,
    stock: offers_models.Stock,
    beneficiary: users_models.User,
) -> typing.Tuple[list[external_bookings_models.Ticket], int]:
    provider = providers_repository.get_provider_enabled_for_pro_by_id(stock.offer.lastProviderId)
    if not provider:
        raise providers_exceptions.InactiveProvider()

    payload = serialize.ExternalEventBookingRequest.build_external_booking(stock, booking, beneficiary)
    response = requests.post(
        provider.bookingExternalUrl, json=payload.json(), headers={"Content-Type": "application/json"}
    )
    _check_external_booking_response_is_ok(response)
    parsed_response = pydantic.parse_obj_as(serialize.ExternalEventBookingResponse, response.json())
    for ticket in parsed_response.tickets:
        add_to_queue(
            REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": ticket.barcode,
                "venue_id": booking.venueId,
                "timestamp": datetime.datetime.utcnow().timestamp(),
            },
        )
    return [
        Ticket(barcode=ticket.barcode, seat_number=ticket.seat) for ticket in parsed_response.tickets
    ], parsed_response.remainingQuantity


def _check_external_booking_response_is_ok(response: requests.Response) -> None:
    if response.status_code == 409:
        try:
            error_response = pydantic.parse_obj_as(serialize.ExternalEventBookingErrorResponse, response.json())
        except (ValueError, pydantic.ValidationError):
            raise exceptions.ExternalBookingException(
                f"External booking failed with status code {response.status_code} and message {response.text}"
            )
        if error_response.error == "sold_out":
            raise exceptions.ExternalBookingSoldOutError()
        if error_response.error == "not_enough_seats" and error_response.remainingQuantity:
            raise exceptions.ExternalBookingNotEnoughSeatsError(remainingQuantity=error_response.remainingQuantity)
    if response.status_code != 201:
        raise exceptions.ExternalBookingException(
            f"External booking failed with status code {response.status_code} and message {response.text}"
        )
