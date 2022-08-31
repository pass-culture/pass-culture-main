import datetime
import logging
from operator import or_
import typing

import pytz
import sentry_sdk
from sqlalchemy import and_
from sqlalchemy.orm import Query

from pcapi.core import search
import pcapi.core.booking_providers.api as booking_providers_api
from pcapi.core.booking_providers.api import _get_venue_booking_provider
from pcapi.core.booking_providers.models import VenueBookingProvider
from pcapi.core.bookings import constants
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import ExternalBooking
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.bookings.repository import generate_booking_token
from pcapi.core.categories import subcategories
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.educational.repository import get_and_lock_collective_stock
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offers import repository as offers_repository
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.models import Stock
from pcapi.core.users.external import update_external_pro
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.utils.cds import get_cds_show_id_from_uuid
from pcapi.workers import push_notification_job
from pcapi.workers import user_emails_job

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
        validation.check_offer_category_is_bookable_by_user(beneficiary, stock)
        validation.check_can_book_free_offer(beneficiary, stock)
        validation.check_offer_already_booked(beneficiary, stock.offer)
        validation.check_quantity(stock.offer, quantity)
        validation.check_stock_is_bookable(stock, quantity)
        total_amount = quantity * stock.price  # type: ignore [operator]
        validation.check_expenses_limits(beneficiary, total_amount, stock.offer)  # type: ignore [arg-type]

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
            status=BookingStatus.CONFIRMED,
        )

        booking.dateCreated = datetime.datetime.utcnow()
        booking.cancellationLimitDate = compute_cancellation_limit_date(stock.beginningDatetime, booking.dateCreated)

        if is_activation_code_applicable:
            booking.activationCode = offers_repository.get_available_activation_code(stock)  # type: ignore [assignment]
            booking.mark_as_used()

        individual_booking = IndividualBooking(
            booking=booking,
            depositId=beneficiary.deposit.id if beneficiary.has_active_deposit else None,  # type: ignore [union-attr]
            userId=beneficiary.id,
        )
        stock.dnBookedQuantity += booking.quantity  # type: ignore [operator]
        _book_external_offer(booking, stock)

        repository.save(individual_booking, stock)

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

    if not transactional_mails.send_user_new_booking_to_pro_email(individual_booking, first_venue_booking):
        logger.warning(
            "Could not send booking confirmation email to offerer",
            extra={"booking": booking.id},
        )
    if not transactional_mails.send_individual_booking_confirmation_email_to_beneficiary(individual_booking):
        logger.warning("Could not send booking=%s confirmation email to beneficiary", booking.id)

    search.async_index_offer_ids([stock.offerId])

    update_external_user(individual_booking.user)
    update_external_pro(stock.offer.venue.bookingEmail)

    return individual_booking.booking


def _book_external_offer(booking: Booking, stock: Stock) -> None:
    is_active_venue_booking_provider = db.session.query(
        VenueBookingProvider.query.filter(
            VenueBookingProvider.venueId == stock.offer.venueId, VenueBookingProvider.isActive
        ).exists()
    ).scalar()

    if (
        FeatureToggle.ENABLE_CDS_IMPLEMENTATION.is_active()
        and stock.offer.subcategory.id == subcategories.SEANCE_CINE.id
        and is_active_venue_booking_provider
    ):
        venue_booking_provider_name = _get_venue_booking_provider(stock.offer.venueId).bookingProvider.name.value
        sentry_sdk.set_tag("venue-booking-provider", venue_booking_provider_name)

        if stock.idAtProviders and get_cds_show_id_from_uuid(stock.idAtProviders).isdigit():
            show_id = int(get_cds_show_id_from_uuid(stock.idAtProviders))
        else:
            logger.error(
                'Stock %d has invalid (non-digit) show_id in idAtProviders "%s"', stock.id, stock.idAtProviders
            )
            raise TypeError("Only digit is allowed for show_id in stock.idAtProviders ")

        tickets = booking_providers_api.book_ticket(
            venue_id=stock.offer.venueId,
            show_id=show_id,
            quantity=booking.quantity,  # type: ignore [arg-type]
        )
        booking.externalBookings = [
            ExternalBooking(barcode=ticket.barcode, seat=ticket.seat_number) for ticket in tickets
        ]


def _cancel_booking(
    booking: Booking,
    reason: BookingCancellationReasons,
    cancel_even_if_used: bool = False,
    raise_if_error: bool = False,
) -> bool:
    """Cancel booking and update a user's credit information on Batch"""
    with transaction():
        stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)  # type: ignore [arg-type]
        db.session.refresh(booking)
        old_status = booking.status
        try:
            booking.cancel_booking(cancel_even_if_used)
            _cancel_external_booking(booking, stock)
        except (BookingIsAlreadyUsed, BookingIsAlreadyCancelled) as e:
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
        if old_status is BookingStatus.USED:
            finance_api.cancel_pricing(booking, finance_models.PricingLogReason.MARK_AS_UNUSED)
        booking.cancellationReason = reason
        stock.dnBookedQuantity -= booking.quantity  # type: ignore [operator]
        repository.save(booking, stock)

    logger.info(  # type: ignore [call-arg]
        "Booking has been cancelled",
        extra={"booking_id": booking.id, "reason": str(reason)},
        technical_message_id="booking.cancelled",
    )

    if booking.individualBooking is not None:
        update_external_user(booking.individualBooking.user)
        update_external_pro(booking.venue.bookingEmail)
    search.async_index_offer_ids([booking.stock.offerId])
    return True


def _cancel_external_booking(booking: Booking, stock: Stock) -> None:
    if (
        FeatureToggle.ENABLE_CDS_IMPLEMENTATION.is_active()
        and stock.offer.subcategory.id == subcategories.SEANCE_CINE.id
        and booking.isExternal
    ):
        barcodes = [external_booking.barcode for external_booking in booking.externalBookings]
        booking_providers_api.cancel_booking(stock.offer.venueId, barcodes)


def _cancel_collective_booking(
    collective_booking: CollectiveBooking,
    reason: CollectiveBookingCancellationReasons,
) -> bool:
    with transaction():
        collective_stock = get_and_lock_collective_stock(stock_id=collective_booking.collectiveStock.id)
        db.session.refresh(collective_booking)
        old_status = collective_booking.status
        try:
            collective_booking.cancel_booking(cancel_even_if_used=True)
        except (BookingIsAlreadyUsed, BookingIsAlreadyCancelled) as e:
            logger.info(
                "%s: %s",
                type(e).__name__,
                str(e),
                extra={
                    "collective_booking": collective_booking.id,
                    "reason": str(reason),
                },
            )
            return False

        if old_status is CollectiveBookingStatus.USED:
            finance_api.cancel_pricing(collective_booking, finance_models.PricingLogReason.MARK_AS_UNUSED)

        collective_booking.cancellationReason = reason
        repository.save(collective_booking, collective_stock)
    logger.info(
        "CollectiveBooking has been cancelled",
        extra={
            "collective_booking": collective_booking.id,
            "reason": str(reason),
        },
    )

    return True


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


def _cancel_collective_booking_from_stock(
    collective_stock: CollectiveStock, reason: CollectiveBookingCancellationReasons
) -> CollectiveBooking | None:
    """
    Cancel booking.
    Note that this will not reindex the stock.offer in Algolia
    """
    booking_to_cancel: CollectiveBooking | None = next(
        (
            collective_booking
            for collective_booking in collective_stock.collectiveBookings  # type: ignore [attr-defined]
            if collective_booking.status not in [CollectiveBookingStatus.CANCELLED, CollectiveBookingStatus.REIMBURSED]
        ),
        None,
    )

    if booking_to_cancel is not None:
        _cancel_collective_booking(booking_to_cancel, reason)

    return booking_to_cancel


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


def cancel_collective_booking_from_stock_by_offerer(
    collective_stock: CollectiveStock,
) -> CollectiveBooking | None:
    cancelled_booking = _cancel_collective_booking_from_stock(
        collective_stock, CollectiveBookingCancellationReasons.OFFERER
    )
    return cancelled_booking


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

    logger.info("Booking was marked as used", extra={"booking_id": booking.id}, technical_message_id="booking.used")  # type: ignore [call-arg]

    if booking.individualBookingId is not None:
        update_external_user(booking.individualBooking.user)  # type: ignore [union-attr]


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
            stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)  # type: ignore [arg-type]
            stock.dnBookedQuantity += booking.quantity  # type: ignore [operator]
            db.session.add(stock)
    db.session.add(booking)
    db.session.commit()
    logger.info("Booking was uncancelled and marked as used", extra={"bookingId": booking.id})

    if booking.individualBookingId is not None:
        update_external_user(booking.individualBooking.user)  # type: ignore [union-attr]


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
    if FeatureToggle.PRICE_BOOKINGS.is_active():
        finance_api.cancel_pricing(booking, finance_models.PricingLogReason.MARK_AS_UNUSED)
    booking.mark_as_unused_set_confirmed()
    repository.save(booking)

    logger.info("Booking was marked as unused", extra={"booking_id": booking.id}, technical_message_id="booking.unused")  # type: ignore [call-arg]

    if booking.individualBookingId is not None:
        update_external_user(booking.individualBooking.user)  # type: ignore [union-attr]
        update_external_pro(booking.venue.bookingEmail)


def get_qr_code_data(booking_token: str) -> str:
    return f"PASSCULTURE:{QR_CODE_PASS_CULTURE_VERSION};TOKEN:{booking_token}"


def compute_cancellation_limit_date(
    event_beginning: datetime.datetime | None, booking_creation_or_event_edition: datetime.datetime
) -> datetime.datetime | None:
    if event_beginning:
        if event_beginning.tzinfo:
            tz_naive_event_beginning = event_beginning.astimezone(pytz.utc)
            tz_naive_event_beginning = tz_naive_event_beginning.replace(tzinfo=None)
        else:
            tz_naive_event_beginning = event_beginning
        before_event_limit = tz_naive_event_beginning - constants.CONFIRM_BOOKING_BEFORE_EVENT_DELAY
        after_booking_or_event_edition_limit = (
            booking_creation_or_event_edition + constants.CONFIRM_BOOKING_AFTER_CREATION_DELAY
        )
        earliest_date_in_cancellation_period = min(before_event_limit, after_booking_or_event_edition_limit)
        latest_date_between_earliest_date_in_cancellation_period_and_booking_creation_or_event_edition = max(
            earliest_date_in_cancellation_period, booking_creation_or_event_edition
        )
        return latest_date_between_earliest_date_in_cancellation_period_and_booking_creation_or_event_edition
    return None


def update_cancellation_limit_dates(
    bookings_to_update: list[Booking], new_beginning_datetime: datetime.datetime
) -> list[Booking]:
    for booking in bookings_to_update:
        booking.cancellationLimitDate = compute_cancellation_limit_date(
            event_beginning=new_beginning_datetime, booking_creation_or_event_edition=datetime.datetime.utcnow()
        )
    repository.save(*bookings_to_update)
    return bookings_to_update


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


def _logs_for_data_purpose(collective_bookings_subquery: Query) -> None:
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
    # fmt: off
    bookings_subquery = (
        Booking.query.join(offers_models.Stock).outerjoin(EducationalBooking)
            .filter(Booking.status.in_((BookingStatus.CONFIRMED, BookingStatus.PENDING)))
            .filter(offers_models.Stock.beginningDatetime < threshold)
            .with_entities(Booking.id)
            .subquery()
    )

    individual_bookings = (
        Booking.query.filter(and_(Booking.id.in_(bookings_subquery), Booking.educationalBookingId.is_(None)))
    )

    educational_bookings = (
        Booking.query.filter(Booking.id.in_(bookings_subquery))
            .filter(
            or_(EducationalBooking.status != EducationalBookingStatus.REFUSED, EducationalBooking.status.is_(None)))
    )

    collective_bookings_subquery = (
        CollectiveBooking.query.join(CollectiveStock)
            .filter(CollectiveBooking.status == CollectiveBookingStatus.CONFIRMED)
            .filter(CollectiveStock.beginningDatetime < threshold)
    )
    collective_bookings = (
        CollectiveBooking.query.filter(CollectiveBooking.id.in_(collective_bookings_subquery.with_entities(CollectiveBooking.id)))
    )

    _logs_for_data_purpose(collective_bookings_subquery)

    # fmt: on
    n_individual_updated = individual_bookings.update(
        {"status": BookingStatus.USED, "dateUsed": now}, synchronize_session=False
    )
    db.session.commit()

    n_educational_updated = educational_bookings.update(
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
            "educationalBookingsUpdatedCount": n_educational_updated,
            "collectiveBookingsUpdatedCount": n_collective_bookings_updated,
        },
    )


def get_individual_bookings_from_stock(stock_id: int) -> typing.Generator[Booking, None, None]:
    query = (
        Booking.query.filter(Booking.stockId == stock_id, Booking.status != BookingStatus.CANCELLED)
        .join(Booking.individualBooking)  # exclude collective bookings
        .with_entities(Booking.id, Booking.userId)
        .distinct()
    )

    for booking in query.yield_per(1_000):
        yield booking
