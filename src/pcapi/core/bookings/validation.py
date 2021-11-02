import datetime
from decimal import Decimal

from pcapi.core.bookings import api
from pcapi.core.bookings import constants
from pcapi.core.bookings import exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import User
from pcapi.models import api_errors
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import payment_queries
from pcapi.utils.date import utc_datetime_to_department_timezone

from ..educational.models import EducationalBookingStatus
from .exceptions import EducationalOfferCannotBeBooked
from .exceptions import NoActivationCodeAvailable


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
        Booking.query.filter_by(
            user=user,
            isCancelled=False,
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


def check_stock_is_bookable(stock: Stock, quantity: int) -> None:
    # The first part already checks that the stock is not sold out,
    # but we need to make sure that we can book `quantity` (which
    # could be 2), hence the second part of the check).
    if not stock.isBookable or (stock.quantity is not None and stock.remainingQuantity < quantity):
        raise exceptions.StockIsNotBookable()


def check_expenses_limits(user: User, requested_amount: Decimal, offer: Offer) -> None:
    """Raise an error if the requested amount would exceed the user's
    expense limits.
    """
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
        raise exceptions.PhysicalExpenseLimitHasBeenReached(domains_credit.physical.initial)


def check_beneficiary_can_cancel_booking(user: User, booking: Booking) -> None:
    if booking.userId != user.id:
        raise exceptions.BookingDoesntExist()
    if booking.isUsed:
        raise exceptions.BookingIsAlreadyUsed()
    if booking.isConfirmed:
        raise exceptions.CannotCancelConfirmedBooking(
            constants.BOOKING_CONFIRMATION_ERROR_CLAUSES["after_creation_delay"],
            constants.BOOKING_CONFIRMATION_ERROR_CLAUSES["before_event_delay"],
        )


# FIXME: should not raise exceptions from `api_errors` (see below for details).
def check_booking_can_be_cancelled(booking: Booking) -> None:
    if booking.isCancelled:
        gone = api_errors.ResourceGoneError()
        gone.add_error("global", "Cette contremarque a déjà été annulée")
        raise gone
    if booking.isUsed:
        forbidden = api_errors.ForbiddenError()
        forbidden.add_error("global", "Impossible d'annuler une réservation consommée")
        raise forbidden


# FIXME (dbaty, 2020-10-19): I moved this function from validation/routes/bookings.py. It
# should not raise HTTP-related exceptions. It should rather raise
# generic exceptions such as `BookingIsAlreadyUsed` and the calling
# route should have an exception handler that turns it into the
# desired HTTP-related exception (such as ResourceGone and Forbidden)
# See also functions below.
def check_is_usable(booking: Booking) -> None:
    if payment_queries.has_payment(booking):
        forbidden = api_errors.ForbiddenError()
        forbidden.add_error("payment", "Cette réservation a été remboursée")
        raise forbidden

    if booking.isUsed or booking.status is BookingStatus.USED:
        gone = api_errors.ResourceGoneError()
        gone.add_error("booking", "Cette réservation a déjà été validée")
        raise gone

    if booking.isCancelled or booking.status is BookingStatus.CANCELLED:
        forbidden = api_errors.ForbiddenError()
        forbidden.add_error("booking", "Cette réservation a été annulée")
        raise forbidden

    if booking.educationalBookingId is not None:
        if booking.educationalBooking.status is EducationalBookingStatus.REFUSED:
            reason = "Cette réservation pour une offre éducationnelle a été refusée par le chef d'établissement"
            raise api_errors.ForbiddenError(errors={"educationalBooking": reason})

        if booking.educationalBooking.status is not EducationalBookingStatus.USED_BY_INSTITUTE:
            reason = (
                "Cette réservation pour une offre éducationnelle n'est pas encore validée par le chef d'établissement"
            )
            raise api_errors.ForbiddenError(errors={"educationalBooking": reason})

    is_booking_for_event_and_not_confirmed = booking.stock.beginningDatetime and not booking.isConfirmed
    if is_booking_for_event_and_not_confirmed:
        forbidden = api_errors.ForbiddenError()
        venue_departement_code = booking.venue.departementCode
        booking_date = datetime.datetime.strftime(
            utc_datetime_to_department_timezone(booking.dateCreated, venue_departement_code), "%d/%m/%Y à %H:%M"
        )
        max_cancellation_date = datetime.datetime.strftime(
            utc_datetime_to_department_timezone(
                api.compute_cancellation_limit_date(
                    booking.stock.beginningDatetime,
                    booking.dateCreated,
                ),
                venue_departement_code,
            ),
            "%d/%m/%Y à %H:%M",
        )

        forbidden.add_error(
            "booking",
            f"Cette réservation a été effectuée le {booking_date}. "
            f"Veuillez attendre jusqu’au {max_cancellation_date} pour valider la contremarque.",
        )
        raise forbidden


# FIXME: should not raise exceptions from `api_errors` (see above for details).
def check_can_be_mark_as_unused(booking: Booking) -> None:
    if (
        booking.stock.canHaveActivationCodes
        and booking.activationCode
        and FeatureToggle.AUTO_ACTIVATE_DIGITAL_BOOKINGS.is_active()
    ):
        forbidden = api_errors.ForbiddenError()
        forbidden.add_error("booking", "Cette réservation ne peut pas être marquée comme inutilisée")
        raise forbidden

    if booking.isCancelled:
        forbidden = api_errors.ForbiddenError()
        forbidden.add_error("booking", "Cette réservation a été annulée")
        raise forbidden

    if payment_queries.has_payment(booking):
        gone = api_errors.ResourceGoneError()
        gone.add_error("payment", "Le remboursement est en cours de traitement")
        raise gone

    if not booking.isUsed:
        gone = api_errors.ResourceGoneError()
        gone.add_error("booking", "Cette réservation n'a pas encore été validée")
        raise gone


def check_activation_code_available(stock: Stock) -> None:
    if offers_repository.get_available_activation_code(stock) is None:
        raise NoActivationCodeAvailable()


def check_offer_is_not_educational(stock: Stock) -> None:
    if stock.offer.isEducational:
        raise EducationalOfferCannotBeBooked()
