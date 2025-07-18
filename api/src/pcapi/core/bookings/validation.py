import datetime
from decimal import Decimal

import pcapi.core.finance.repository as finance_repository
import pcapi.utils.date as date_utils
from pcapi.core.bookings import constants
from pcapi.core.bookings import exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models import db

from .exceptions import NoActivationCodeAvailable
from .exceptions import OfferCategoryNotBookableByUser


def check_can_book_free_offer(user: User, stock: Stock) -> None:
    # XXX: Despite its name, the intent of this function is to check
    # whether the user is allowed to book any offer (free or not
    # free), i.e. whether the user is a pro/admin or a "regular
    # user". Here we seem to allow pro/admin users to book non-free
    # offers, but in fact we'll check later whether the user has
    # money; since pro/admin users don't, an exception will be raised.
    if not user.is_beneficiary and stock.price == 0:
        raise exceptions.CannotBookFreeOffers()


def check_offer_already_booked(user: User, offer: Offer) -> None:
    """Raise ``OfferIsAlreadyBooked`` if the user already booked this offer."""
    if db.session.query(
        db.session.query(Booking)
        .filter(
            Booking.user == user,
            Booking.status != BookingStatus.CANCELLED,
        )
        .join(Stock)
        .filter(Stock.offerId == offer.id)
        .exists()
    ).scalar():
        raise exceptions.OfferIsAlreadyBooked()


def check_quantity(offer: Offer, quantity: int) -> None:
    """May raise QuantityIsInvalid, depending on ``offer.isDuo``."""
    if offer.isDuo and quantity not in (1, 2):
        raise exceptions.QuantityIsInvalid("Vous devez réserver une place ou deux dans le cas d'une offre DUO.")

    if not offer.isDuo and quantity != 1:
        raise exceptions.QuantityIsInvalid("Vous ne pouvez réserver qu'une place pour cette offre.")


def _stock_can_be_booked(stock: Stock) -> bool:
    starting_from = stock.offer.bookingAllowedDatetime
    if not starting_from:
        return True

    timezoned_starting_from = date_utils.default_timezone_to_local_datetime(starting_from, "UTC")
    return timezoned_starting_from <= datetime.datetime.now(datetime.timezone.utc)


def check_stock_is_bookable(stock: Stock, quantity: int) -> None:
    # The first part already checks that the stock is not sold out,
    # but we need to make sure that we can book `quantity` (which
    # could be 2), hence the second part of the check).
    # Also, a stock can be booked only if its offer bookingAllowedDatetime
    # is past.
    if (
        not stock.isBookable
        or (stock.quantity is not None and stock.remainingQuantity < quantity)
        or not _stock_can_be_booked(stock)
    ):
        raise exceptions.StockIsNotBookable()


def check_expenses_limits(user: User, requested_amount: Decimal, offer: Offer) -> None:
    """Raise an error if the requested amount would exceed the user's
    expense limits.
    """
    from pcapi.core.users.api import get_domains_credit  # avoid circular import

    domains_credit = get_domains_credit(user)
    deposit = user.deposit
    if not domains_credit or not deposit:
        raise exceptions.UserHasInsufficientFunds()

    if requested_amount > domains_credit.all.remaining:
        raise exceptions.UserHasInsufficientFunds()

    if (
        domains_credit.digital
        and deposit.specific_caps.digital_cap_applies(offer)
        and requested_amount > domains_credit.digital.remaining
    ):
        raise exceptions.DigitalExpenseLimitHasBeenReached(domains_credit.digital.initial)

    if (
        domains_credit.physical
        and deposit.specific_caps.physical_cap_applies(offer)
        and requested_amount > domains_credit.physical.remaining
    ):
        raise exceptions.PhysicalExpenseLimitHasBeenReached(int(domains_credit.physical.initial))


def check_beneficiary_can_cancel_booking(user: User, booking: Booking) -> None:
    if booking.userId != user.id:
        raise exceptions.BookingDoesntExist()
    if booking.isCancelled:
        raise exceptions.BookingIsCancelled()
    if booking.is_used_or_reimbursed:
        raise exceptions.BookingIsAlreadyUsed()
    check_booking_cancellation_limit_date(booking)


def check_booking_can_be_cancelled(booking: Booking) -> None:
    if booking.status == BookingStatus.CANCELLED:
        raise exceptions.BookingIsAlreadyCancelled()
    if booking.status == BookingStatus.REIMBURSED:
        raise exceptions.BookingIsAlreadyRefunded()
    if booking.status == BookingStatus.USED:
        raise exceptions.BookingIsAlreadyUsed()


def check_booking_cancellation_limit_date(booking: Booking) -> None:
    if booking.isConfirmed:
        raise exceptions.CannotCancelConfirmedBooking(
            constants.BOOKING_CONFIRMATION_ERROR_CLAUSES["after_creation_delay"],
            constants.BOOKING_CONFIRMATION_ERROR_CLAUSES["before_event_delay"],
        )


def check_is_usable(booking: Booking) -> None:
    if finance_repository.has_reimbursement(booking):
        raise exceptions.BookingIsAlreadyRefunded()

    if booking.status is BookingStatus.USED:
        raise exceptions.BookingIsAlreadyUsed()

    if booking.status is BookingStatus.CANCELLED:
        raise exceptions.BookingIsAlreadyCancelled()

    if booking.offerer.isClosed:
        raise exceptions.OffererIsClosed()

    is_booking_for_event_and_not_confirmed = booking.stock.beginningDatetime and not booking.isConfirmed
    if is_booking_for_event_and_not_confirmed:
        if booking.cancellationLimitDate is None:
            raise ValueError("Can't compute max_cancellation_date with None as cancellationLimitDate")
        # TODO bdalbianco 02/06/2025: CLEAN_OA remove check when no virtual venue
        offer_department_code = (
            booking.stock.offer.offererAddress.address.departmentCode if booking.stock.offer.offererAddress else None
        )
        max_cancellation_date = datetime.datetime.strftime(
            date_utils.utc_datetime_to_department_timezone(
                booking.cancellationLimitDate,
                offer_department_code,
            ),
            "%d/%m/%Y à %H:%M",
        )
        raise exceptions.BookingIsNotConfirmed(
            f"Vous pourrez valider cette contremarque à partir du {max_cancellation_date}, une fois le délai d’annulation passé."
        )


def check_can_be_mark_as_unused(booking: Booking) -> None:
    if booking.stock.canHaveActivationCodes and booking.activationCode:
        raise exceptions.BookingHasActivationCode()

    if booking.status == BookingStatus.CANCELLED:
        raise exceptions.BookingIsAlreadyCancelled()

    if finance_repository.has_reimbursement(booking):
        raise exceptions.BookingIsAlreadyRefunded()

    if booking.status is not BookingStatus.USED:
        raise exceptions.BookingIsNotUsed()


def check_activation_code_available(stock: Stock) -> None:
    if offers_repository.get_available_activation_code(stock) is None:
        raise NoActivationCodeAvailable()


def check_offer_category_is_bookable_by_user(user: User, stock: Stock) -> None:
    if user.has_beneficiary_role:
        return

    if stock.is_forbidden_to_underage:
        raise OfferCategoryNotBookableByUser()
