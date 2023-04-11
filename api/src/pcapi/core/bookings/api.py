import datetime
import logging
import typing

import sentry_sdk
import sqlalchemy as sa

from pcapi.analytics.amplitude import events as amplitude_events
from pcapi.core import search
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import ExternalBooking
from pcapi.core.bookings.repository import generate_booking_token
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.external.attributes.api import update_external_user
import pcapi.core.external_bookings.api as external_bookings_api
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offers import repository as offers_repository
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.models import Stock
import pcapi.core.offers.validation as offers_validation
import pcapi.core.providers.repository as providers_repository
from pcapi.core.users.models import User
from pcapi.core.users.repository import get_and_lock_user
from pcapi.models import db
from pcapi.models import feature
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository import transaction
import pcapi.serialization.utils as serialization_utils
import pcapi.utils.cinema_providers as cinema_providers_utils
from pcapi.workers import push_notification_job
from pcapi.workers import user_emails_job

from . import constants
from . import exceptions
from . import validation
from .exceptions import BookingIsAlreadyCancelled
from .exceptions import BookingIsAlreadyUsed


logger = logging.getLogger(__name__)

QR_CODE_PASS_CULTURE_VERSION = "v3"


def book_offer(
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

        first_venue_booking = not db.session.query(
            Booking.query.filter(Booking.venueId == stock.offer.venueId).exists()
        ).scalar()

        # FIXME (dbaty, 2020-10-20): if we directly set relations (for
        # example with `booking.user = beneficiary`) instead of foreign keys,
        # the session tries to add the object when `get_user_expenses()`
        # is called because autoflush is enabled. As such, the PostgreSQL
        # exceptions (tooManyBookings and insufficientFunds) may raise at
        # this point and will bubble up. If we want them to be caught, we
        # have to set foreign keys, so that the session is NOT autoflushed
        # in `get_user_expenses` and is only committed in `repository.save()`
        # where exceptions are caught. Since we are using flask-sqlalchemy,
        # I don't think that we should use autoflush, nor should we use
        # the `pcapi.repository.repository` module.
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
            depositId=beneficiary.deposit.id if beneficiary.has_active_deposit else None,  # type: ignore [union-attr]
        )

        booking.dateCreated = datetime.datetime.utcnow()
        booking.cancellationLimitDate = compute_booking_cancellation_limit_date(
            stock.beginningDatetime, booking.dateCreated
        )

        if is_activation_code_applicable:
            booking.activationCode = offers_repository.get_available_activation_code(stock)  # type: ignore [assignment]
            booking.mark_as_used()

        stock.dnBookedQuantity += booking.quantity

        is_external_ticket_applicable = providers_repository.is_external_ticket_applicable(stock.offer)

        if is_external_ticket_applicable:
            if not offers_validation.check_offer_is_from_current_cinema_provider(stock.offer):
                raise ValueError("This offer is from the wrong cinema provider")
            _book_external_ticket(booking, stock, beneficiary)

        repository.save(booking, stock)

    logger.info(
        "Beneficiary booked an offer",
        extra={
            "actor": beneficiary.id,
            "offer": stock.offerId,
            "stock": stock.id,
            "booking": booking.id,
            "used": booking.is_used_or_reimbursed,
        },
    )
    amplitude_events.track_book_offer_event(booking)

    if not transactional_mails.send_user_new_booking_to_pro_email(booking, first_venue_booking):
        logger.warning(
            "Could not send booking confirmation email to offerer",
            extra={"booking": booking.id},
        )
    if not transactional_mails.send_individual_booking_confirmation_email_to_beneficiary(booking):
        logger.warning("Could not send booking=%s confirmation email to beneficiary", booking.id)

    search.async_index_offer_ids([stock.offerId])

    update_external_user(booking.user)
    update_external_pro(stock.offer.venue.bookingEmail)

    return booking


def _book_external_ticket(booking: Booking, stock: Stock, beneficiary: User) -> None:
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
        case _:
            raise ValueError(f"Unknown Provider: {venue_provider_name}")

    show_id = cinema_providers_utils.get_showtime_id_from_uuid(stock.idAtProviders, venue_provider_name)
    if not show_id:
        raise ValueError("Could not retrieve show_id")

    tickets = external_bookings_api.book_ticket(
        venue_id=stock.offer.venueId, show_id=show_id, booking=booking, beneficiary=beneficiary
    )
    booking.externalBookings = [ExternalBooking(barcode=ticket.barcode, seat=ticket.seat_number) for ticket in tickets]


def _cancel_booking(
    booking: Booking,
    reason: BookingCancellationReasons,
    cancel_even_if_used: bool = False,
    raise_if_error: bool = False,
) -> bool:
    """Cancel booking and update a user's credit information on Batch"""
    with transaction():
        stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)
        db.session.refresh(booking)
        try:
            finance_api.cancel_pricing(booking, finance_models.PricingLogReason.MARK_AS_UNUSED)
            booking.cancel_booking(reason, cancel_even_if_used)
            _cancel_external_booking(booking, stock)
        except (BookingIsAlreadyUsed, BookingIsAlreadyCancelled, finance_exceptions.NonCancellablePricingError) as e:
            if raise_if_error:
                raise
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
        repository.save(booking, stock)

    logger.info(
        "Booking has been cancelled",
        extra={"booking_id": booking.id, "reason": str(reason)},
        technical_message_id="booking.cancelled",
    )
    amplitude_events.track_cancel_booking_event(booking, reason)

    update_external_user(booking.user)
    update_external_pro(booking.venue.bookingEmail)
    search.async_index_offer_ids([booking.stock.offerId])
    return True


def _cancel_external_booking(booking: Booking, stock: Stock) -> None:
    if not booking.isExternal:
        return None
    venue_provider_name = external_bookings_api.get_active_cinema_venue_provider(
        stock.offer.venueId
    ).provider.localClass
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
        case _:
            raise ValueError(f"Unknown Provider: {venue_provider_name}")
    barcodes = [external_booking.barcode for external_booking in booking.externalBookings]
    external_bookings_api.cancel_booking(stock.offer.venueId, barcodes)


def _cancel_bookings_from_stock(stock: offers_models.Stock, reason: BookingCancellationReasons) -> list[Booking]:
    """
    Cancel multiple bookings and update the users' credit information on Batch.
    Note that this will not reindex the stock.offer in Algolia
    """
    deleted_bookings: list[Booking] = []
    for booking in stock.bookings:
        if _cancel_booking(booking, reason, cancel_even_if_used=typing.cast(bool, stock.offer.isEvent)):
            deleted_bookings.append(booking)

    return deleted_bookings


def cancel_booking_by_beneficiary(user: User, booking: Booking) -> None:
    if not user.is_beneficiary:
        raise RuntimeError("Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s" % user)
    validation.check_beneficiary_can_cancel_booking(user, booking)
    _cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)
    user_emails_job.send_booking_cancellation_emails_to_user_and_offerer_job.delay(booking.id)


def cancel_booking_by_offerer(booking: Booking) -> None:
    validation.check_booking_can_be_cancelled(booking)
    _cancel_booking(booking, BookingCancellationReasons.OFFERER)
    push_notification_job.send_cancel_booking_notification.delay([booking.id])
    user_emails_job.send_booking_cancellation_emails_to_user_and_offerer_job.delay(booking.id)


def cancel_bookings_from_stock_by_offerer(stock: offers_models.Stock) -> list[Booking]:
    cancelled_bookings = _cancel_bookings_from_stock(stock, BookingCancellationReasons.OFFERER)
    search.async_index_offer_ids([stock.offerId])
    return cancelled_bookings


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
    _cancel_booking(booking, BookingCancellationReasons.FRAUD)
    logger.info("Cancelled booking for fraud reason", extra={"booking": booking.id})

    if not transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason):  # type: ignore [arg-type]
        logger.warning(
            "Could not send booking cancellation emails to offerer",
            extra={"booking": booking.id},
        )


def cancel_booking_on_user_requested_account_suspension(booking: Booking) -> None:
    validation.check_booking_can_be_cancelled(booking)
    _cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)
    logger.info("Cancelled booking on user-requested account suspension", extra={"booking": booking.id})

    if not transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason):  # type: ignore [arg-type]
        logger.warning(
            "Could not send booking= cancellation emails to offerer and beneficiary",
            extra={"booking": booking.id},
        )


def mark_as_used(booking: Booking) -> None:
    validation.check_is_usable(booking)
    booking.mark_as_used()
    repository.save(booking)

    logger.info("Booking was marked as used", extra={"booking_id": booking.id}, technical_message_id="booking.used")
    amplitude_events.track_mark_as_used_event(booking)

    update_external_user(booking.user)


def mark_as_used_with_uncancelling(booking: Booking) -> None:
    """Mark a booking as used from cancelled status.

    This function should be called only if the booking
    has been cancelled by mistake or fraudulently after the offer was
    retrieved (for example, when a beneficiary retrieved a book from a
    library and then cancelled their booking before the library marked
    it as used).
    """
    # I'm not 100% sure the transaction is required here
    # It is not clear to me wether or not Flask-SQLAlchemy will make
    # a rollback if we raise a validation exception.
    # Since I lock the stock, I really want to make sure the lock is
    # removed ASAP.
    with transaction():
        if booking.status == BookingStatus.CANCELLED:
            booking.uncancel_booking_set_used()
            stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)
            stock.dnBookedQuantity += booking.quantity
            db.session.add(stock)
    db.session.add(booking)
    db.session.commit()
    logger.info("Booking was uncancelled and marked as used", extra={"bookingId": booking.id})

    update_external_user(booking.user)


def mark_as_cancelled(booking: Booking) -> None:
    """
    A booking can be cancelled only if it has not been cancelled before and if
    it has not been refunded. Since a payment can be retried, it is safer to
    say that a booking with payment, whatever its status, should be considered
    refunded. A used booking without payment can be marked as cancelled by an
    admin user.
    """
    if booking.status == BookingStatus.CANCELLED:
        raise exceptions.BookingIsAlreadyCancelled()

    if finance_repository.has_reimbursement(booking):
        raise exceptions.BookingIsAlreadyRefunded()

    _cancel_booking(booking, BookingCancellationReasons.BENEFICIARY, cancel_even_if_used=True, raise_if_error=True)
    transactional_mails.send_booking_cancellation_by_beneficiary_to_pro_email(booking)


def mark_as_unused(booking: Booking) -> None:
    validation.check_can_be_mark_as_unused(booking)
    finance_api.cancel_pricing(booking, finance_models.PricingLogReason.MARK_AS_UNUSED)
    booking.mark_as_unused_set_confirmed()
    repository.save(booking)

    logger.info("Booking was marked as unused", extra={"booking_id": booking.id}, technical_message_id="booking.unused")

    update_external_user(booking.user)
    update_external_pro(booking.venue.bookingEmail)


def get_qr_code_data(booking_token: str) -> str:
    return f"PASSCULTURE:{QR_CODE_PASS_CULTURE_VERSION};TOKEN:{booking_token}"


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
            event_beginning=new_beginning_datetime, edition_date=datetime.datetime.utcnow()
        )
    repository.save(*bookings_to_update)
    return bookings_to_update


def _compute_edition_cancellation_limit_date(
    event_beginning: datetime.datetime, edition_date: datetime.datetime
) -> datetime.datetime:
    after_edition_cancellation_date = edition_date + constants.CONFIRM_BOOKING_AFTER_CREATION_DELAY
    return min(event_beginning, after_edition_cancellation_date)


def recompute_dnBookedQuantity(stock_ids: list[int]) -> None:
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
    db.session.execute(query, {"stock_ids": tuple(stock_ids)})


def _logs_for_data_purpose(collective_bookings_subquery: sa.orm.Query) -> None:
    bookings_information_tuple = collective_bookings_subquery.with_entities(
        CollectiveBooking.id, CollectiveBooking.collectiveStockId
    )
    for booking_id, stock_id in bookings_information_tuple:
        educational_utils.log_information_for_data_purpose(
            event_name="BookingUsed",
            extra_data={"bookingId": booking_id, "stockId": stock_id},
        )


def auto_mark_as_used_after_event() -> None:
    """Automatically mark as used bookings that correspond to events that
    have happened (with a delay).
    """
    if not FeatureToggle.UPDATE_BOOKING_USED.is_active():
        raise ValueError("This function is behind a deactivated feature flag.")

    now = datetime.datetime.utcnow()
    threshold = now - constants.AUTO_USE_AFTER_EVENT_TIME_DELAY
    bookings_subquery = (
        Booking.query.join(offers_models.Stock)
        .filter(Booking.status == BookingStatus.CONFIRMED)
        .filter(offers_models.Stock.beginningDatetime < threshold)
        .with_entities(Booking.id)
        .subquery()
    )

    individual_bookings = Booking.query.filter(Booking.id.in_(bookings_subquery))

    collective_bookings_subquery = (
        CollectiveBooking.query.join(CollectiveStock)
        .filter(CollectiveBooking.status == CollectiveBookingStatus.CONFIRMED)
        .filter(CollectiveStock.beginningDatetime < threshold)
    )
    collective_bookings = CollectiveBooking.query.filter(
        CollectiveBooking.id.in_(collective_bookings_subquery.with_entities(CollectiveBooking.id))
    )

    _logs_for_data_purpose(collective_bookings_subquery)

    n_individual_updated = individual_bookings.update(
        {"status": BookingStatus.USED, "dateUsed": now}, synchronize_session=False
    )
    db.session.commit()

    n_collective_bookings_updated = collective_bookings.update(
        {"status": CollectiveBookingStatus.USED, "dateUsed": now}, synchronize_session=False
    )
    db.session.commit()

    logger.info(
        "Automatically marked bookings as used after event",
        extra={
            "individualBookingsUpdatedCount": n_individual_updated,
            "collectiveBookingsUpdatedCount": n_collective_bookings_updated,
        },
    )


def get_individual_bookings_from_stock(stock_id: int) -> typing.Generator[Booking, None, None]:
    query = (
        Booking.query.filter(Booking.stockId == stock_id, Booking.status != BookingStatus.CANCELLED)
        .with_entities(Booking.id, Booking.userId)
        .distinct()
    )

    for booking in query.yield_per(1_000):
        yield booking


def archive_old_activation_code_bookings() -> None:
    old_bookings = Booking.query.join(Booking.stock, Stock.offer, Booking.activationCode).filter(
        offers_models.Offer.isDigital.is_(True),  # type: ignore [attr-defined]
        offers_models.ActivationCode.id.isnot(None),
        Booking.dateCreated < datetime.datetime.utcnow() - constants.ARCHIVE_DELAY,
    )
    number_updated = Booking.query.filter(Booking.id.in_(old_bookings.with_entities(Booking.id))).update(
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
