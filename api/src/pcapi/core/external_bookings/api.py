import datetime
import json
import logging

import pydantic.v1 as pydantic_v1

from pcapi import settings
from pcapi.core.bookings.constants import REDIS_EXTERNAL_BOOKINGS_NAME
from pcapi.core.bookings.constants import RedisExternalBookingType
import pcapi.core.bookings.models as bookings_models
from pcapi.core.bookings.utils import generate_hmac_signature
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
from pcapi.models import db
from pcapi.models import feature
import pcapi.tasks.external_api_booking_notification_tasks as external_api_booking_notification
from pcapi.tasks.serialization.external_api_booking_notification_tasks import BookingAction
from pcapi.tasks.serialization.external_api_booking_notification_tasks import ExternalApiBookingNotificationRequest
from pcapi.utils import requests
from pcapi.utils.queue import add_to_queue

from . import exceptions
from . import serialize
from . import validation


logger = logging.getLogger(__name__)

EXTERNAL_BOOKINGS_FF = (
    feature.FeatureToggle.DISABLE_BOOST_EXTERNAL_BOOKINGS,
    feature.FeatureToggle.DISABLE_CDS_EXTERNAL_BOOKINGS,
    feature.FeatureToggle.DISABLE_CGR_EXTERNAL_BOOKINGS,
    feature.FeatureToggle.DISABLE_EMS_EXTERNAL_BOOKINGS,
)


def get_shows_stock(venue_id: int, shows_id: list[int]) -> dict[str, int]:
    client = _get_external_bookings_client_api(venue_id)
    return client.get_shows_remaining_places(shows_id)


def get_movie_stocks(venue_id: int, movie_id: str) -> dict[str, int]:
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


def disable_external_bookings() -> None:
    feature.Feature.query.filter(feature.Feature.name.in_([ff.name for ff in EXTERNAL_BOOKINGS_FF])).update(
        {"isActive": True}, synchronize_session=False
    )
    db.session.commit()


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
    provider: providers_models.Provider,
    venue_provider: providers_models.VenueProvider | None,
) -> tuple[list[external_bookings_models.Ticket], int | None]:
    validation.check_ticketing_service_is_correctly_set(provider=provider, venue_provider=venue_provider)

    payload = serialize.ExternalEventBookingRequest.build_external_booking(stock, booking, beneficiary)
    json_payload = payload.json()
    hmac_signature = generate_hmac_signature(provider.hmacKey, json_payload)

    # Booking Url (Venue booking url > provider booking url)
    booking_url = provider.bookingExternalUrl

    if venue_provider and venue_provider.externalUrls and venue_provider.externalUrls.bookingExternalUrl:
        booking_url = venue_provider.externalUrls.bookingExternalUrl

    response = requests.post(
        booking_url,
        json=json_payload,
        hmac=hmac_signature,
        headers={"Content-Type": "application/json"},
    )
    _check_external_booking_response_is_ok(response)

    try:
        parsed_response = pydantic_v1.parse_obj_as(serialize.ExternalEventBookingResponse, response.json())
    except (pydantic_v1.ValidationError, json.JSONDecodeError) as err:
        logger.exception(
            "Could not parse external booking response",
            extra={"status_code": response.status_code, "response": response.text, "error": err},
        )
        raise exceptions.ExternalBookingException("External booking failed.")
    parsed_response.tickets = _verify_and_return_tickets_with_same_quantity_as_booking(
        parsed_response.tickets, booking, stock, venue_provider
    )

    for ticket in parsed_response.tickets:
        add_to_queue(
            REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": ticket.barcode,
                "timestamp": datetime.datetime.utcnow().timestamp(),
                "booking_type": RedisExternalBookingType.EVENT,
                "cancel_event_info": {
                    "provider_id": provider.id,
                    "stock_id": stock.id,
                },
            },
        )

    return [
        Ticket(barcode=ticket.barcode, seat_number=ticket.seat) for ticket in parsed_response.tickets
    ], parsed_response.remainingQuantity


def _verify_and_return_tickets_with_same_quantity_as_booking(
    tickets: list[serialize.ExternalEventTicket],
    booking: bookings_models.Booking,
    stock: offers_models.Stock,
    venue_provider: providers_models.VenueProvider | None,
) -> list[serialize.ExternalEventTicket]:
    if len(tickets) == booking.quantity:
        return tickets
    if len(tickets) == 2 and booking.quantity == 1:
        add_to_queue(
            REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": tickets[0].barcode,
                "timestamp": datetime.datetime.utcnow().timestamp(),
                "booking_type": RedisExternalBookingType.EVENT,
                "cancel_event_info": {
                    "provider_id": stock.offer.lastProvider.id,
                    "stock_id": stock.id,
                },
            },
        )
        return [tickets[1]]
    if len(tickets) == 1 and booking.quantity == 2:
        cancel_event_ticket(stock.offer.lastProvider, stock, [tickets[0].barcode], False, venue_provider)
        raise exceptions.ExternalBookingException(
            "External booking failed with status code 201 but only one ticket was returned for duo reservation"
        )
    raise exceptions.ExternalBookingException(
        f"External booking failed with status code 201 but {len(tickets)} tickets were returned instead of {booking.quantity}"
    )


def cancel_event_ticket(
    provider: providers_models.Provider,
    stock: offers_models.Stock,
    barcodes: list[str],
    is_booking_saved: bool,
    venue_provider: providers_models.VenueProvider | None,
) -> None:
    validation.check_ticketing_service_is_correctly_set(provider=provider, venue_provider=venue_provider)

    payload = serialize.ExternalEventCancelBookingRequest.build_external_cancel_booking(barcodes)
    json_payload = payload.json()
    hmac_signature = generate_hmac_signature(provider.hmacKey, json_payload)
    headers = {"Content-Type": "application/json"}

    # Cancel Url (Venue cancel url > provider cancel url)
    cancel_url = provider.cancelExternalUrl

    if venue_provider and venue_provider.externalUrls and venue_provider.externalUrls.cancelExternalUrl:
        cancel_url = venue_provider.externalUrls.cancelExternalUrl

    response = requests.post(cancel_url, json=json_payload, headers=headers, hmac=hmac_signature)
    _check_external_booking_response_is_ok(response)

    try:
        parsed_response = pydantic_v1.parse_obj_as(serialize.ExternalEventCancelBookingResponse, response.json())
        if parsed_response.remainingQuantity is None:
            stock.quantity = None
        else:
            new_quantity = parsed_response.remainingQuantity + stock.dnBookedQuantity
            if is_booking_saved:
                new_quantity -= len(barcodes)
            stock.quantity = new_quantity
    except (ValueError, pydantic_v1.ValidationError):
        logger.exception(
            "Could not parse external booking cancel response",
            extra={"status_code": response.status_code, "response": response.text},
        )


def send_booking_notification_to_external_service(booking: bookings_models.Booking, action: BookingAction) -> None:
    """
    Send booking notification (cancel or booking) to provider external service.

    Do not send notification when:
        - notification params are not properly set (missing `hmacKey` or/and `notificationExternalUrl`)
        - booking is linked to an external ticketing system
    """
    hmacKey, notification_url = _get_notification_params(booking)
    notification_system_not_set = not hmacKey or not notification_url

    booking_is_linked_to_ticketing_system = (
        booking.stock.offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP
    )

    if booking_is_linked_to_ticketing_system or notification_system_not_set:
        return

    try:
        external_api_notification_request = ExternalApiBookingNotificationRequest.build(booking, action)
        signature = generate_hmac_signature(hmacKey, external_api_notification_request.json())  # type: ignore[arg-type]
        payload = external_api_booking_notification.ExternalApiBookingNotificationTaskPayload(
            data=external_api_notification_request,
            notificationUrl=notification_url,  # type: ignore[arg-type]
            signature=signature,
        )
        external_api_booking_notification.external_api_booking_notification_task.delay(payload)
    except Exception as err:  # pylint: disable=broad-except
        logger.exception(
            "Error: %s. Could not send external booking notification for: booking: %s, action %s",
            err,
            action.value,
            booking.id,
        )


def _get_notification_params(booking: bookings_models.Booking) -> tuple[str | None, str | None]:
    """
    Return (`hmacKey`, `notificationExternalUrl`) necessary to notify provider
    """
    provider = providers_repository.get_provider_enabled_for_pro_by_id(booking.stock.offer.lastProviderId)

    if not provider:  # provider not enabled
        return None, None

    notification_url = provider.notificationExternalUrl
    venue_provider = providers_repository.get_venue_provider_by_venue_and_provider_ids(
        booking.stock.offer.venueId,
        provider.id,
    )

    # `notificationExternalUrl` defined at venue level has priority over `notificationExternalUrl` defined at provider level
    if venue_provider and venue_provider.externalUrls and venue_provider.externalUrls.notificationExternalUrl:
        notification_url = venue_provider.externalUrls.notificationExternalUrl

    return provider.hmacKey, notification_url


def _check_external_booking_response_is_ok(response: requests.Response) -> None:
    if response.status_code == 409:
        try:
            error_response = pydantic_v1.parse_obj_as(serialize.ExternalEventBookingErrorResponse, response.json())
        except (ValueError, pydantic_v1.ValidationError):
            raise exceptions.ExternalBookingException(
                f"External booking failed with status code {response.status_code} and message {response.text}"
            )
        if error_response.error == "sold_out":
            raise exceptions.ExternalBookingSoldOutError()
        if error_response.error == "not_enough_seats" and isinstance(error_response.remainingQuantity, int):
            raise exceptions.ExternalBookingNotEnoughSeatsError(remainingQuantity=error_response.remainingQuantity)
        if error_response.error == "already_cancelled":
            raise exceptions.ExternalBookingAlreadyCancelledError(remainingQuantity=error_response.remainingQuantity)
    if not response.ok:
        raise exceptions.ExternalBookingException(
            f"External booking failed with status code {response.status_code} and message {response.text}"
        )
