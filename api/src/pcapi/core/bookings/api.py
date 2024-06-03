import datetime
from functools import partial
import json
import logging
import typing

from flask import current_app
import sentry_sdk
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from pcapi.connectors.ems import EMSAPIException
from pcapi.core import search
from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import BookingValidationAuthorType
from pcapi.core.bookings.models import ExternalBooking
from pcapi.core.bookings.repository import generate_booking_token
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.external import batch
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.batch import track_offer_booked_event
import pcapi.core.external_bookings.api as external_bookings_api
from pcapi.core.external_bookings.ems import constants as ems_constants
from pcapi.core.external_bookings.ems.client import EMSClientAPI
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import repository as offers_repository
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.exceptions as offers_exceptions
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory
from pcapi.core.offers.models import PriceCategoryLabel
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
import pcapi.core.offers.validation as offers_validation
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.repository as providers_repository
from pcapi.core.users.models import User
from pcapi.core.users.repository import get_and_lock_user
from pcapi.models import db
from pcapi.models import feature
from pcapi.models.feature import FeatureToggle
from pcapi.repository import is_managed_transaction
from pcapi.repository import mark_transaction_as_invalid
from pcapi.repository import on_commit
from pcapi.repository import repository
from pcapi.repository import transaction
import pcapi.serialization.utils as serialization_utils
import pcapi.tasks.external_api_booking_notification_tasks as external_api_booking_notification
from pcapi.tasks.serialization.external_api_booking_notification_tasks import BookingAction
from pcapi.tasks.serialization.external_api_booking_notification_tasks import ExternalApiBookingNotificationRequest
from pcapi.utils import queue
import pcapi.utils.cinema_providers as cinema_providers_utils
from pcapi.utils.requests import exceptions as requests_exceptions
from pcapi.workers import push_notification_job
from pcapi.workers import user_emails_job

from . import constants
from . import exceptions
from . import utils
from . import validation
from .exceptions import BookingIsAlreadyCancelled
from .exceptions import BookingIsAlreadyUsed


logger = logging.getLogger(__name__)


def _is_ended_booking(booking: Booking) -> bool:
    if (
        booking.stock.beginningDatetime
        and booking.status != BookingStatus.CANCELLED
        and booking.stock.beginningDatetime >= datetime.datetime.utcnow()
    ):
        # consider future events as "ongoing" even if they are used
        return False

    if (booking.stock.canHaveActivationCodes and booking.activationCode) or booking.display_even_if_used:
        # consider digital bookings and free offer from defined subcategories as special: is_used should be true anyway so
        # let's use displayAsEnded
        return bool(booking.displayAsEnded)

    return (
        not booking.stock.offer.isPermanent
        if booking.is_used_or_reimbursed
        else booking.status == BookingStatus.CANCELLED
    )


def get_individual_bookings(user: User) -> list[Booking]:
    """
    Get all bookings for a user, with all the data needed for the bookings page
    including the offer and venue data.
    """
    return (
        Booking.query.filter_by(userId=user.id)
        .options(joinedload(Booking.stock).load_only(Stock.id, Stock.beginningDatetime, Stock.price, Stock.features))
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .load_only(
                Offer.bookingContact,
                Offer.name,
                Offer.url,
                Offer.subcategoryId,
                Offer.withdrawalDetails,
                Offer.withdrawalType,
                Offer.withdrawalDelay,
                Offer.extraData,
            )
            .joinedload(Offer.product)
            .load_only(
                Product.id,
                Product.thumbCount,
            )
            .joinedload(Product.productMediations)
        )
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.priceCategory)
            .joinedload(PriceCategory.priceCategoryLabel)
            .load_only(PriceCategoryLabel.label)
        )
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .joinedload(Offer.venue)
            .load_only(
                Venue.name,
                Venue.street,
                Venue.postalCode,
                Venue.city,
                Venue.latitude,
                Venue.longitude,
                Venue.publicName,
                Venue.timezone,
            )
        )
        .options(joinedload(Booking.stock).joinedload(Stock.offer).joinedload(Offer.mediations))
        .options(joinedload(Booking.activationCode))
        .options(joinedload(Booking.externalBookings))
        .options(joinedload(Booking.deposit).load_only(finance_models.Deposit.type))
    ).all()


def classify_and_sort_bookings(
    individual_bookings: list[Booking],
) -> tuple[list[Booking], list[Booking]]:
    """
    Classify bookings between ended and ongoing bookings
    """
    ended_bookings = []
    ongoing_bookings = []
    for booking in individual_bookings:
        if _is_ended_booking(booking):
            ended_bookings.append(booking)
        else:
            ongoing_bookings.append(booking)
            booking.qrCodeData = utils.get_qr_code_data(booking.token)

    sorted_ended_bookings = sorted(
        ended_bookings,
        key=lambda b: b.stock.beginningDatetime or b.dateUsed or b.cancellationDate or datetime.datetime.min,
        reverse=True,
    )
    # put permanent bookings at the end with datetime.max
    sorted_ongoing_bookings = sorted(
        ongoing_bookings,
        key=lambda b: (
            b.expirationDate or b.stock.beginningDatetime or datetime.datetime.max,
            -b.id,
        ),
    )
    return (sorted_ended_bookings, sorted_ongoing_bookings)


def _book_offer(
    beneficiary: User,
    stock_id: int,
    quantity: int,
) -> Booking:
    """
    Return a booking or raise an exception if it's not possible.
    Update a user's credit information on Batch.
    """
    # The call to transaction here ensures we free the FOR UPDATE lock
    # on the stock if validation issues an exception
    with transaction():
        stock = offers_repository.get_and_lock_stock(stock_id=stock_id)
        get_and_lock_user(beneficiary.id)
        validation.check_offer_category_is_bookable_by_user(beneficiary, stock)
        validation.check_can_book_free_offer(beneficiary, stock)
        validation.check_offer_already_booked(beneficiary, stock.offer)
        validation.check_quantity(stock.offer, quantity)
        validation.check_stock_is_bookable(stock, quantity)
        total_amount = quantity * stock.price
        validation.check_expenses_limits(beneficiary, total_amount, stock.offer)

        is_activation_code_applicable = (
            stock.canHaveActivationCodes
            and db.session.query(offers_models.ActivationCode.query.filter_by(stock=stock).exists()).scalar()
        )
        if is_activation_code_applicable:
            validation.check_activation_code_available(stock)

        booking = Booking(
            userId=beneficiary.id,
            stockId=stock.id,
            amount=stock.price,
            quantity=quantity,
            token=generate_booking_token(),
            venueId=stock.offer.venueId,
            offererId=stock.offer.venue.managingOffererId,
            priceCategoryLabel=(
                stock.priceCategory.priceCategoryLabel.label if getattr(stock, "priceCategory") else None
            ),
            status=BookingStatus.CONFIRMED,
            depositId=(
                beneficiary.deposit.id if (beneficiary.has_active_deposit and beneficiary.deposit is not None) else None
            ),
        )

        booking.dateCreated = datetime.datetime.utcnow()
        booking.cancellationLimitDate = compute_booking_cancellation_limit_date(
            stock.beginningDatetime, booking.dateCreated
        )

        if is_activation_code_applicable:
            booking.activationCode = offers_repository.get_available_activation_code(stock)
            booking.mark_as_used(BookingValidationAuthorType.AUTO)
        if stock.is_automatically_used:
            booking.mark_as_used(BookingValidationAuthorType.AUTO)

        is_cinema_external_ticket_applicable = providers_repository.is_cinema_external_ticket_applicable(stock.offer)

        if is_cinema_external_ticket_applicable:
            offers_validation.check_offer_is_from_current_cinema_provider(stock.offer)
            _book_cinema_external_ticket(booking, stock, beneficiary)

        if providers_repository.is_event_external_ticket_applicable(stock.offer):
            remaining_quantity = _book_event_external_ticket(booking, stock, beneficiary)
            if remaining_quantity is None:
                stock.quantity = None
            else:
                stock.quantity = stock.dnBookedQuantity + remaining_quantity + booking.quantity

        stock.dnBookedQuantity += booking.quantity

        logger.info(
            "Updating dnBookedQuantity after a successful booking",
            extra={
                "booking_id": booking.id,
                "booking_quantity": booking.quantity,
                "stock_dnBookedQuantity": stock.dnBookedQuantity,
            },
        )

        db.session.add_all((booking, stock))
        db.session.flush()  # to setup relations on `booking` for `add_event()` below.

        if booking.status == BookingStatus.USED:
            finance_api.add_event(
                finance_models.FinanceEventMotive.BOOKING_USED,
                booking=booking,
            )
    return booking


def book_offer(
    beneficiary: User,
    stock_id: int,
    quantity: int,
) -> Booking:
    """
    Return a booking or raise an exception if it's not possible.
    Update a user's credit information on Batch.
    """
    stock = offers_models.Stock.query.filter_by(id=stock_id).one_or_none()
    if not stock:
        raise offers_exceptions.StockDoesNotExist()

    first_venue_booking = not db.session.query(
        Booking.query.filter(Booking.venueId == stock.offer.venueId).exists()
    ).scalar()

    try:
        booking = _book_offer(beneficiary, stock_id, quantity)
    except external_bookings_exceptions.ExternalBookingNotEnoughSeatsError as error:
        offers_api.edit_stock(
            stock,
            quantity=(stock.dnBookedQuantity + error.remainingQuantity),
            editing_provider=stock.offer.lastProvider,
        )
        db.session.commit()
        logger.info(
            "Could not book offer: Event has not enough seats left",
            extra={"offer_id": stock.offer.id, "provider_id": stock.offer.lastProviderId},
        )
        raise
    except external_bookings_exceptions.ExternalBookingSoldOutError:
        offers_api.edit_stock(stock, quantity=stock.dnBookedQuantity, editing_provider=stock.offer.lastProvider)
        db.session.commit()
        logger.info(
            "Could not book offer: Event sold out",
            extra={"offer_id": stock.offer.id, "provider_id": stock.offer.lastProviderId},
        )
        raise

    logger.info(
        "Beneficiary booked an offer",
        extra={
            "actor": beneficiary.id,
            "offer": stock.offerId,
            "stock": stock.id,
            "booking": booking.id,
            "used": booking.is_used_or_reimbursed,
            "booking_token": booking.token,
            "barcodes": [external_booking.barcode for external_booking in booking.externalBookings],
            "booking_quantity": booking.quantity,
            "stock_dnBookedQuantity": stock.dnBookedQuantity,
            "stock_quantity": stock.quantity,
        },
    )
    track_offer_booked_event(beneficiary.id, stock.offer)
    _send_external_booking_notification_if_necessary(booking, BookingAction.BOOK)

    transactional_mails.send_user_new_booking_to_pro_email(booking, first_venue_booking)
    transactional_mails.send_individual_booking_confirmation_email_to_beneficiary(booking)

    search.async_index_offer_ids(
        [stock.offerId],
        reason=search.IndexationReason.BOOKING_CREATION,
    )

    update_external_user(booking.user)
    update_external_pro(stock.offer.venue.bookingEmail)

    return booking


def _book_cinema_external_ticket(booking: Booking, stock: Stock, beneficiary: User) -> None:
    venue_provider_name = external_bookings_api.get_active_cinema_venue_provider(
        stock.offer.venueId
    ).provider.localClass
    sentry_sdk.set_tag("cinema-venue-provider", venue_provider_name)

    match venue_provider_name:
        case "CDSStocks":
            if not FeatureToggle.ENABLE_CDS_IMPLEMENTATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_CDS_IMPLEMENTATION is inactive")
            if FeatureToggle.DISABLE_CDS_EXTERNAL_BOOKINGS.is_active():
                raise feature.DisabledFeatureError("DISABLE_CDS_EXTERNAL_BOOKINGS is active")
        case "BoostStocks":
            if not FeatureToggle.ENABLE_BOOST_API_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_BOOST_API_INTEGRATION is inactive")
            if FeatureToggle.DISABLE_BOOST_EXTERNAL_BOOKINGS.is_active():
                raise feature.DisabledFeatureError("DISABLE_BOOST_EXTERNAL_BOOKINGS is active")
        case "CGRStocks":
            if not FeatureToggle.ENABLE_CGR_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_CGR_INTEGRATION is inactive")
            if FeatureToggle.DISABLE_CGR_EXTERNAL_BOOKINGS.is_active():
                raise feature.DisabledFeatureError("DISABLE_CGR_EXTERNAL_BOOKINGS is active")
        case "EMSStocks":
            if not FeatureToggle.ENABLE_EMS_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_EMS_INTEGRATION is inactive")
            if FeatureToggle.DISABLE_EMS_EXTERNAL_BOOKINGS.is_active():
                raise feature.DisabledFeatureError("DISABLE_EMS_EXTERNAL_BOOKINGS is active")
        case _:
            raise providers_exceptions.UnknownProvider(f"Unknown Provider: {venue_provider_name}")
    show_id = cinema_providers_utils.get_showtime_id_from_uuid(stock.idAtProviders, venue_provider_name)
    if not show_id:
        raise providers_exceptions.ShowIdNotFound("Could not retrieve show_id")
    try:
        tickets = external_bookings_api.book_cinema_ticket(
            venue_id=stock.offer.venueId,
            show_id=show_id,
            booking=booking,
            beneficiary=beneficiary,
        )
    except external_bookings_exceptions.ExternalBookingSoldOutError as exc:
        logger.exception("Could not book this offer as it's sold out.")
        raise exc
    except Exception as exc:
        logger.exception("Could not book external ticket: %s", exc)
        raise external_bookings_exceptions.ExternalBookingException

    booking.externalBookings = [
        ExternalBooking(
            barcode=ticket.barcode, seat=ticket.seat_number, additional_information=ticket.additional_information
        )
        for ticket in tickets
    ]
    logger.info(
        "Successfully booked an offer",
        extra={
            "booking_id": booking.id,
            "booking_token": booking.token,
            "barcodes": [external_booking.barcode for external_booking in booking.externalBookings],
        },
    )


def _book_event_external_ticket(booking: Booking, stock: Stock, beneficiary: User) -> int | None:
    provider = providers_repository.get_provider_enabled_for_pro_by_id(stock.offer.lastProviderId)
    if not provider:
        raise providers_exceptions.InactiveProvider()

    sentry_sdk.set_tag("external-provider", provider.name)
    try:
        tickets, remaining_quantity = external_bookings_api.book_event_ticket(booking, stock, beneficiary, provider)
    except external_bookings_exceptions.ExternalBookingException as exc:
        logger.exception("Could not book external ticket: %s", exc)
        raise exc

    booking.externalBookings = [ExternalBooking(barcode=ticket.barcode, seat=ticket.seat_number) for ticket in tickets]
    return remaining_quantity


def _cancel_booking(
    booking: Booking,
    reason: BookingCancellationReasons,
    cancel_even_if_used: bool = False,
    raise_if_error: bool = False,
    one_side_cancellation: bool = False,
) -> bool:
    """Cancel booking and update a user's credit information on Batch"""
    try:
        if not _execute_cancel_booking(booking, reason, cancel_even_if_used, raise_if_error, one_side_cancellation):
            return False
    except external_bookings_exceptions.ExternalBookingAlreadyCancelledError as error:
        booking.cancel_booking(reason, cancel_even_if_used)
        if error.remainingQuantity is None:
            booking.stock.quantity = None
        else:
            booking.stock.quantity = booking.stock.dnBookedQuantity + error.remainingQuantity
    except external_bookings_exceptions.ExternalBookingException as error:
        if raise_if_error:
            raise error

    logger.info(
        "Booking has been cancelled",
        extra={
            "booking_id": booking.id,
            "reason": str(reason),
            "booking_token": booking.token,
            "barcodes": [external_booking.barcode for external_booking in booking.externalBookings],
        },
        technical_message_id="booking.cancelled",
    )
    batch.track_booking_cancellation(booking)
    _send_external_booking_notification_if_necessary(booking, BookingAction.CANCEL)

    update_external_user(booking.user)
    update_external_pro(booking.venue.bookingEmail)
    on_commit(
        partial(
            search.async_index_offer_ids,
            [booking.stock.offerId],
            reason=search.IndexationReason.BOOKING_CANCELLATION,
        )
    )
    return True


def _execute_cancel_booking(
    booking: Booking,
    reason: BookingCancellationReasons,
    cancel_even_if_used: bool = False,
    raise_if_error: bool = False,
    one_side_cancellation: bool = False,
) -> bool:
    with transaction():
        with db.session.no_autoflush:
            stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)
            db.session.refresh(booking)
            logger.info(
                "Cancelling booking...",
                extra={
                    "booking_id": booking.id,
                    "stock_dnBookedQuantity": stock.dnBookedQuantity,
                    "booking_quantity": booking.quantity,
                },
            )
            try:
                cancelled_event = finance_api.cancel_latest_event(booking)
                booking.cancel_booking(reason, cancel_even_if_used)
                if cancelled_event:
                    finance_api.add_event(
                        finance_models.FinanceEventMotive.BOOKING_CANCELLED_AFTER_USE,
                        booking=booking,
                    )
                if not one_side_cancellation:
                    _cancel_external_booking(booking, stock)
            except (
                BookingIsAlreadyUsed,
                BookingIsAlreadyCancelled,
                finance_exceptions.NonCancellablePricingError,
            ) as e:
                if raise_if_error:
                    raise
                if is_managed_transaction():
                    mark_transaction_as_invalid()
                else:
                    db.session.rollback()
                logger.info(
                    "%s: %s",
                    type(e).__name__,
                    str(e),
                    extra={
                        "booking": booking.id,
                        "reason": str(reason),
                    },
                )
                return False
            stock.dnBookedQuantity -= booking.quantity
            if booking.activationCode and stock.quantity:
                stock.quantity -= 1
            repository.save(booking, stock)
    return True


def _send_external_booking_notification_if_necessary(booking: Booking, action: BookingAction) -> None:
    provider = providers_repository.get_provider_enabled_for_pro_by_id(booking.stock.offer.lastProviderId)
    if (
        booking.stock.offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP
        or not provider
        or not provider.notificationExternalUrl
    ):
        return

    try:
        external_api_notification_request = ExternalApiBookingNotificationRequest.build(booking, action)
        signature = utils.generate_hmac_signature(provider.hmacKey, external_api_notification_request.json())
        payload = external_api_booking_notification.ExternalApiBookingNotificationTaskPayload(
            data=external_api_notification_request,
            notificationUrl=provider.notificationExternalUrl,
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


def _cancel_external_booking(booking: Booking, stock: Stock) -> None:
    offer = stock.offer

    if not booking.isExternal:
        return None

    if offer.lastProvider and offer.lastProvider.hasProviderEnableCharlie:
        sentry_sdk.set_tag("external-provider", offer.lastProvider.name)
        barcodes = [external_booking.barcode for external_booking in booking.externalBookings]
        try:
            external_bookings_api.cancel_event_ticket(offer.lastProvider, stock, barcodes, True)
        except external_bookings_exceptions.ExternalBookingException:
            logger.exception("Could not cancel external ticket")
            raise external_bookings_exceptions.ExternalBookingException
        except external_bookings_exceptions.ExternalBookingAlreadyCancelledError as error:
            logger.info("External ticket already cancelled for booking: %s. Error %s", booking.id, str(error))
            raise error
        return None

    venue_provider_name = external_bookings_api.get_active_cinema_venue_provider(offer.venueId).provider.localClass
    sentry_sdk.set_tag("cinema-venue-provider", venue_provider_name)
    match venue_provider_name:
        case "CDSStocks":
            if not FeatureToggle.ENABLE_CDS_IMPLEMENTATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_CDS_IMPLEMENTATION is inactive")
        case "BoostStocks":
            if not FeatureToggle.ENABLE_BOOST_API_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_BOOST_API_INTEGRATION is inactive")
        case "CGRStocks":
            if not FeatureToggle.ENABLE_CGR_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_CGR_INTEGRATION is inactive")
        case "EMSStocks":
            if not FeatureToggle.ENABLE_EMS_INTEGRATION.is_active():
                raise feature.DisabledFeatureError("ENABLE_EMS_INTEGRATION is inactive")
        case _:
            raise offers_exceptions.UnexpectedCinemaProvider(f"Unknown Provider: {venue_provider_name}")
    barcodes = [external_booking.barcode for external_booking in booking.externalBookings]
    external_bookings_api.cancel_booking(stock.offer.venueId, barcodes)


def _cancel_bookings_from_stock(
    stock: offers_models.Stock, reason: BookingCancellationReasons, one_side_cancellation: bool = False
) -> list[Booking]:
    """
    Cancel multiple bookings and update the users' credit information on Batch.
    Note that this will not reindex the stock.offer in Algolia
    """
    deleted_bookings: list[Booking] = []
    for booking in stock.bookings:
        if _cancel_booking(
            booking,
            reason,
            cancel_even_if_used=typing.cast(bool, stock.offer.isEvent),
            one_side_cancellation=one_side_cancellation,
        ):
            deleted_bookings.append(booking)

    return deleted_bookings


def cancel_booking_by_beneficiary(user: User, booking: Booking) -> None:
    if not user.is_beneficiary:
        raise RuntimeError("Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s" % user)
    validation.check_beneficiary_can_cancel_booking(user, booking)
    _cancel_booking(booking, BookingCancellationReasons.BENEFICIARY, raise_if_error=True)
    user_emails_job.send_booking_cancellation_emails_to_user_and_offerer_job.delay(booking.id)


def cancel_booking_by_offerer(booking: Booking) -> None:
    validation.check_booking_can_be_cancelled(booking)
    _cancel_booking(booking, BookingCancellationReasons.OFFERER, raise_if_error=True)
    push_notification_job.send_cancel_booking_notification.delay([booking.id])
    user_emails_job.send_booking_cancellation_emails_to_user_and_offerer_job.delay(booking.id)


def cancel_bookings_from_stock_by_offerer(stock: offers_models.Stock) -> list[Booking]:
    return _cancel_bookings_from_stock(stock, BookingCancellationReasons.OFFERER, one_side_cancellation=True)


def cancel_bookings_from_rejected_offer(offer: offers_models.Offer) -> list[Booking]:
    cancelled_bookings = []
    for stock in offer.stocks:
        cancelled_bookings.extend(_cancel_bookings_from_stock(stock, BookingCancellationReasons.FRAUD))
    logger.info(
        "Cancelled bookings for rejected offer",
        extra={
            "bookings": [b.id for b in cancelled_bookings],
            "offer": offer.id,
        },
    )

    return cancelled_bookings


def cancel_booking_for_fraud(booking: Booking) -> None:
    validation.check_booking_can_be_cancelled(booking)
    cancelled = _cancel_booking(booking, BookingCancellationReasons.FRAUD)
    if not cancelled:
        return
    logger.info("Cancelled booking for fraud reason", extra={"booking": booking.id})
    transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)


def cancel_booking_on_user_requested_account_suspension(booking: Booking) -> None:
    validation.check_booking_can_be_cancelled(booking)
    cancelled = _cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)
    if not cancelled:
        return
    logger.info(
        "Cancelled booking on user-requested account suspension",
        extra={"booking": booking.id},
    )
    transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)


def mark_as_used(booking: Booking, validation_author_type: BookingValidationAuthorType) -> None:
    validation.check_is_usable(booking)
    booking.mark_as_used(validation_author_type)
    finance_api.add_event(
        finance_models.FinanceEventMotive.BOOKING_USED,
        booking=booking,
    )
    repository.save(booking)

    logger.info(
        "Booking was marked as used",
        extra={"booking_id": booking.id},
        technical_message_id="booking.used",
    )

    update_external_user(booking.user)


def mark_as_used_with_uncancelling(booking: Booking, validation_author_type: BookingValidationAuthorType) -> None:
    """Mark a booking as used from cancelled status.

    This function should be called only if the booking
    has been cancelled by mistake or fraudulently after the offer was
    retrieved (for example, when a beneficiary retrieved a book from a
    library and then cancelled their booking before the library marked
    it as used).
    """
    # I'm not 100% sure the transaction is required here
    # It is not clear to me whether or not Flask-SQLAlchemy will make
    # a rollback if we raise a validation exception.
    # Since I lock the stock, I really want to make sure the lock is
    # removed ASAP.
    if (
        booking.deposit
        and booking.deposit.expirationDate
        and booking.deposit.expirationDate < datetime.datetime.utcnow()
    ):
        raise bookings_exceptions.BookingDepositCreditExpired()

    if booking.status == BookingStatus.CANCELLED:
        booking.uncancel_booking_set_used()
        stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)
        stock.dnBookedQuantity += booking.quantity
        db.session.add(stock)
        db.session.flush()
    booking.validationAuthorType = validation_author_type
    db.session.add(booking)
    finance_api.add_event(
        finance_models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION,
        booking=booking,
    )

    db.session.flush()
    logger.info("Booking was uncancelled and marked as used", extra={"bookingId": booking.id})

    update_external_user(booking.user)


def mark_as_cancelled(
    booking: Booking, reason: BookingCancellationReasons, one_side_cancellation: bool = False
) -> None:
    """
    A booking can be cancelled only if it has not been cancelled before and if
    it has not been refunded. Since a payment can be retried, it is safer to
    say that a booking with payment, whatever its status, should be considered
    refunded. A used booking without payment can be marked as cancelled by an
    admin user.

    One side cancellation. Mainly to be used from the backoffice. The external provider API
    is not called and the booking is cancelled on our side.
    """
    if booking.status == BookingStatus.CANCELLED:
        raise exceptions.BookingIsAlreadyCancelled()

    if finance_repository.has_reimbursement(booking):
        raise exceptions.BookingIsAlreadyRefunded()

    if one_side_cancellation:
        if (
            reason != BookingCancellationReasons.BACKOFFICE
            or (
                booking.stock.offer.lastProvider
                and booking.stock.offer.lastProvider.localClass
                not in constants.ONE_SIDE_BOOKINGS_CANCELLATION_PROVIDERS
            )
            or (
                booking.stock.beginningDatetime
                and booking.stock.beginningDatetime < datetime.datetime.utcnow() - datetime.timedelta(days=15)
            )
        ):
            raise exceptions.OneSideCancellationForbidden()

    _cancel_booking(
        booking, reason, cancel_even_if_used=True, raise_if_error=True, one_side_cancellation=one_side_cancellation
    )

    if one_side_cancellation:
        logging.info("External booking cancelled unilaterally", extra={"booking_id": booking.id})
        assert booking.stock.beginningDatetime
        if booking.stock.beginningDatetime < datetime.datetime.utcnow():
            transactional_mails.send_booking_cancelled_unilaterally_provider_support_email(booking)
        else:
            transactional_mails.send_booking_cancellation_by_beneficiary_to_pro_email(booking, one_side_cancellation)
    else:
        transactional_mails.send_booking_cancellation_by_beneficiary_to_pro_email(booking)


def mark_as_unused(booking: Booking) -> None:
    validation.check_can_be_mark_as_unused(booking)
    finance_api.cancel_latest_event(booking)
    finance_api.add_event(
        finance_models.FinanceEventMotive.BOOKING_UNUSED,
        booking=booking,
    )
    booking.mark_as_unused_set_confirmed()
    repository.save(booking)

    logger.info(
        "Booking was marked as unused",
        extra={"booking_id": booking.id},
        technical_message_id="booking.unused",
    )

    update_external_user(booking.user)
    update_external_pro(booking.venue.bookingEmail)


def compute_booking_cancellation_limit_date(
    event_beginning: datetime.datetime | None, booking_date: datetime.datetime
) -> datetime.datetime | None:
    if event_beginning is None:
        return None

    event_beginning = serialization_utils.as_utc_without_timezone(event_beginning)
    before_event_cancellation_date = event_beginning - constants.CONFIRM_BOOKING_BEFORE_EVENT_DELAY
    after_booking_cancellation_date = booking_date + constants.CONFIRM_BOOKING_AFTER_CREATION_DELAY

    earliest_cancellation_date = min(before_event_cancellation_date, after_booking_cancellation_date)

    return max(earliest_cancellation_date, booking_date)


def update_cancellation_limit_dates(
    bookings_to_update: list[Booking], new_beginning_datetime: datetime.datetime
) -> list[Booking]:
    for booking in bookings_to_update:
        booking.cancellationLimitDate = _compute_edition_cancellation_limit_date(
            event_beginning=new_beginning_datetime,
            edition_date=datetime.datetime.utcnow(),
        )
    repository.save(*bookings_to_update)
    return bookings_to_update


def _compute_edition_cancellation_limit_date(
    event_beginning: datetime.datetime, edition_date: datetime.datetime
) -> datetime.datetime:
    after_edition_cancellation_date = edition_date + constants.CONFIRM_BOOKING_AFTER_CREATION_DELAY
    return min(event_beginning, after_edition_cancellation_date)


def recompute_dnBookedQuantity(stock_ids: list[int]) -> None:
    """
    Changes are not committed within this function, use db.session.commit() if necessary.
    """
    query = f"""
      WITH bookings_per_stock AS (
        SELECT
          stock.id AS stock_id,
          COALESCE(SUM(booking.quantity), 0) AS total_bookings
        FROM stock
        -- The `NOT status CANCELLED` condition MUST be part of the JOIN.
        -- If it were part of the WHERE clause, that would exclude
        -- stocks that only have cancelled bookings.
        LEFT OUTER JOIN booking
          ON booking."stockId" = stock.id
          AND booking.status != '{BookingStatus.CANCELLED.value}'
        WHERE stock.id IN :stock_ids
        GROUP BY stock.id
      )
      UPDATE stock
      SET "dnBookedQuantity" = bookings_per_stock.total_bookings
      FROM bookings_per_stock
      WHERE stock.id = bookings_per_stock.stock_id
    """
    db.session.execute(sa.text(query), {"stock_ids": tuple(stock_ids)})


def auto_mark_as_used_after_event() -> None:
    """Automatically mark as used bookings that correspond to events that
    have happened (with a delay).
    """
    if not FeatureToggle.UPDATE_BOOKING_USED.is_active():
        raise ValueError("This function is behind a deactivated feature flag.")

    now = datetime.datetime.utcnow()
    threshold = now - constants.AUTO_USE_AFTER_EVENT_TIME_DELAY

    # Revisit with SQLAlchemy 2.
    #
    # I tried to update and select bookings in a single query, like this:
    #     WITH updated AS (
    #       UPDATE booking
    #       SET "dateUsed" = :now, status = 'USED'
    #       FROM stock WHERE ...
    #       RETURNING booking.id
    #     )
    #     SELECT ... FROM booking JOIN ...
    #     WHERE booking.id IN (select id from updated)
    #
    # In SQLAlchemy:
    #     individual_updated = (
    #         sa.update(Booking)
    #         .returning(Booking.id)
    #         .where(
    #             Booking.status == BookingStatus.CONFIRMED,
    #             Booking.stockId == offers_models.Stock.id,
    #             offers_models.Stock.beginningDatetime < threshold,
    #         )
    #         .values(dateUsed=now, status=BookingStatus.USED)
    #     )
    #     individual_select = sa.select(Booking).options(
    #         sa.orm.joinedload(Booking.stock, innerjoin=True),
    #         sa.orm.joinedload(Booking.venue, innerjoin=True),
    #     )
    #     individual_bookings = db.session.execute(
    #         individual_select.where(Booking.id.in_(sa.select([individual_updated.cte(name="updated").c.id]))),
    #         execution_options={"synchronize_session": True},
    #     )
    #
    # But it does not work: the SELECT part does not see updated
    # columns (and here we need to see the newly set value of
    # `dateUsed`, otherwise `finance.api.add_event()` raises an
    # error).
    #
    # I think that it might be possible to make it work by using
    # `returning(Booking)` instead of `returning(Booking.id)`, and
    # joining related tables. SQLAlchemy would know that what it gets
    # from the CTE must be used to populate `Booking` objects.
    # However, this is only possible in SQLAlchemy 2.

    # Individual bookings: update and add a finance event for each one.
    db.session.execute(
        sa.update(Booking)
        .where(
            Booking.status == BookingStatus.CONFIRMED,
            Booking.stockId == offers_models.Stock.id,
            offers_models.Stock.beginningDatetime < threshold,
        )
        .values(dateUsed=now, status=BookingStatus.USED, validationAuthorType=BookingValidationAuthorType.AUTO),
        execution_options={"synchronize_session": False},
    )
    # `dateUsed` is precise enough that it's very unlikely to get a
    # booking that was marked as used from another channel (and that
    # would already have an event). If it happened, `add_event` would
    # fail because of the PostgreSQL partially unique constraint on
    # `bookingId`.
    individual_bookings = Booking.query.filter_by(dateUsed=now).options(
        sa.orm.joinedload(Booking.stock, innerjoin=True),
        sa.orm.joinedload(Booking.venue, innerjoin=True),
    )
    n_individual_bookings_updated = 0
    for booking in individual_bookings:
        finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED,
            booking=booking,
        )
        n_individual_bookings_updated += 1

    # Collective bookings: update and add a finance event for each
    # one. We do the same as above, except that we add a log for data
    # analysis.
    db.session.execute(
        sa.update(CollectiveBooking)
        .where(
            CollectiveBooking.status == CollectiveBookingStatus.CONFIRMED,
            CollectiveBooking.collectiveStockId == CollectiveStock.id,
            CollectiveStock.beginningDatetime < threshold,
        )
        .values(dateUsed=now, status=CollectiveBookingStatus.USED),
        execution_options={"synchronize_session": False},
    )
    collective_bookings = CollectiveBooking.query.filter_by(dateUsed=now).options(
        sa.orm.joinedload(CollectiveBooking.collectiveStock, innerjoin=True),
        sa.orm.joinedload(CollectiveBooking.venue, innerjoin=True),
    )
    n_collective_bookings_updated = 0
    for booking in collective_bookings:
        finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED,
            booking=booking,
        )
        n_collective_bookings_updated += 1
        educational_utils.log_information_for_data_purpose(
            event_name="BookingUsed",
            extra_data={"bookingId": booking.id, "stockId": booking.collectiveStockId},
            uai=None,
            user_role=None,
        )

    db.session.commit()

    logger.info(
        "Automatically marked bookings as used after event",
        extra={
            "dateUsed": now,
            "individualBookingsUpdatedCount": n_individual_bookings_updated,
            "collectiveBookingsUpdatedCount": n_collective_bookings_updated,
        },
    )


def get_individual_bookings_from_stock(
    stock_id: int,
) -> typing.Generator[Booking, None, None]:
    query = (
        Booking.query.filter(Booking.stockId == stock_id, Booking.status != BookingStatus.CANCELLED)
        .with_entities(Booking.id, Booking.userId)
        .distinct()
    )
    yield from query.yield_per(1_000)


def archive_old_bookings() -> None:
    date_condition = Booking.dateCreated < datetime.datetime.utcnow() - constants.ARCHIVE_DELAY

    query_old_booking_ids = (
        Booking.query.join(Booking.stock)
        .join(Stock.offer)
        .join(Booking.activationCode)
        .filter(date_condition)
        .filter(
            offers_models.Offer.isDigital,
            offers_models.ActivationCode.id.is_not(None),
        )
        .with_entities(Booking.id)
        .union(
            Booking.query.join(Booking.stock)
            .join(Stock.offer)
            .filter(date_condition)
            .filter(Booking.display_even_if_used)
            .with_entities(Booking.id)
        )
    )

    number_updated = Booking.query.filter(Booking.id.in_(query_old_booking_ids)).update(
        {"displayAsEnded": True},
        synchronize_session=False,
    )
    db.session.commit()

    logger.info(
        "Old activation code bookings archived (displayAsEnded=True)",
        extra={
            "archivedBookings": number_updated,
        },
    )


def cancel_unstored_external_bookings() -> None:
    """
    Cancel external bookings if we don't have a corresponding Booking object on our side.
        When a user wants to book an offer that can be booked by an external partner, we first request a booking
        from the partner, and then we try to create a Booking in our database.
        If the second action fails, we need to request the partner to cancel the booking on their side. To do that,
        we push the information to a Redis queue, and regularly check whether we have a corresponding Booking.
    To avoid cancel external bookings in process of pass culture booking, we check if the barcode has an age of 1 min
    in the queue, if it doesn't it will be enqueued again and wait for the next time.
    """
    while True:
        external_booking_info = queue.pop_from_queue(constants.REDIS_EXTERNAL_BOOKINGS_NAME)
        if not external_booking_info:
            break
        if (
            datetime.datetime.utcnow().timestamp() - external_booking_info["timestamp"]
            < constants.EXTERNAL_BOOKINGS_MINIMUM_ITEM_AGE_IN_QUEUE
        ):
            queue.add_to_queue(
                constants.REDIS_EXTERNAL_BOOKINGS_NAME,
                external_booking_info,
                at_head=True,
            )
            break

        barcode = external_booking_info["barcode"]
        external_bookings = ExternalBooking.query.filter_by(barcode=barcode).all()
        if not external_bookings:
            booking_type = external_booking_info.get("booking_type")
            if booking_type == constants.RedisExternalBookingType.EVENT:
                provider_id = external_booking_info["cancel_event_info"]["provider_id"]
                provider = providers_repository.get_provider_enabled_for_pro_by_id(provider_id)
                stock_id = external_booking_info["cancel_event_info"]["stock_id"]
                stock = offers_models.Stock.query.filter_by(id=stock_id).one_or_none()
                if not stock or not provider:
                    logger.error("Couldn't find stock or provider for external booking", extra=external_booking_info)
                    raise external_bookings_exceptions.ExternalBookingException(
                        "Error while canceling unstored ticket. Barcode: ",
                        str(barcode),
                    )
                external_bookings_api.cancel_event_ticket(provider, stock, [barcode], False)
            else:
                venue_id = int(external_booking_info["venue_id"])
                external_bookings_api.cancel_booking(venue_id, [barcode])


def cancel_ems_external_bookings() -> None:
    EMS_DEADLINE_BEFORE_CANCELLING = 90
    redis_client = current_app.redis_client
    ems_queue = ems_constants.EMS_EXTERNAL_BOOKINGS_TO_CANCEL

    while redis_client.llen(ems_queue) > 0:
        booking_to_cancel = json.loads(redis_client.rpop(ems_queue))
        cinema_id, token, timestamp = (
            booking_to_cancel["cinema_id"],
            booking_to_cancel["token"],
            booking_to_cancel["timestamp"],
        )

        if timestamp + EMS_DEADLINE_BEFORE_CANCELLING > datetime.datetime.utcnow().timestamp():
            # This is the oldest booking to cancel we have in the queue and its too recent.
            redis_client.rpush(ems_queue, json.dumps(booking_to_cancel))
            return

        client = EMSClientAPI(cinema_id=cinema_id)
        try:
            tickets = client.get_ticket(token)
        except EMSAPIException as exc:
            logger.info(
                "Fail to fetch the external booking informations with exception: %s",
                str(exc),
                extra={"token": token, "cinema_id": cinema_id},
            )
            continue

        try:
            client.cancel_booking_with_tickets(tickets)
        except (requests_exceptions.ReadTimeout, requests_exceptions.Timeout):
            logger.info(
                "Fail to cancel external booking due to timeout", extra={"token": token, "cinema_id": cinema_id}
            )
        except EMSAPIException as exc:
            logger.info(
                "Fail to cancel external booking due to EMSAPIException: %s",
                str(exc),
                extra={"token": token, "cinema_id": cinema_id},
            )
