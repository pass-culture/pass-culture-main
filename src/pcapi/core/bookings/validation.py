import datetime
import pytz

from pcapi.core.bookings import conf
from pcapi.core.bookings import exceptions
from pcapi.core.bookings.models import Booking
import pcapi.domain.expenses as payments_api
from pcapi.domain import user_activation
from pcapi.models import api_errors, UserSQLEntity
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.db import db
from pcapi.repository import payment_queries


def check_can_book_free_offer(user, stock):
    # XXX: Despite its name, the intent of this function is to check
    # whether the user is allowed to book any offer (free or not
    # free), i.e. whether the user is a pro/admin or a "regular
    # user". Here we seem to allow pro/admin users to book non-free
    # offers, but in fact we'll check later whether the user has
    # money; since pro/admin users don't, an exception will be raised.
    if not user.canBookFreeOffers and stock.price == 0:
        raise exceptions.CannotBookFreeOffers()


def check_offer_already_booked(user, offer):
    """Raise ``OfferIsAlreadyBooked`` if the user already booked this offer."""
    if (
        db.session.query(
            Booking.query
            .filter_by(
                user=user,
                isCancelled=False,
            )
            .join(StockSQLEntity)
            .filter(StockSQLEntity.offerId == offer.id)
            .exists()
        )
        .scalar()
    ):
        raise exceptions.OfferIsAlreadyBooked()


def check_quantity(offer, quantity):
    """May raise QuantityIsInvalid, depending on ``offer.isDuo``."""
    if offer.isDuo and quantity not in (1, 2):
        raise exceptions.QuantityIsInvalid(
            "Vous devez réserver une place ou deux dans le cas d'une offre DUO."
        )

    if not offer.isDuo and quantity != 1:
        raise exceptions.QuantityIsInvalid(
            "Vous ne pouvez réserver qu'une place pour cette offre."
        )


def check_stock_is_bookable(stock):
    if not stock.isBookable:
        raise exceptions.StockIsNotBookable()


def check_expenses_limits(expenses, requested_amount, offer):
    """Raise an error if the requested amount would exceed the user's
    expense limits.
    """
    if (expenses['all']['actual'] + requested_amount) > expenses['all']['max']:
        raise exceptions.UserHasInsufficientFunds()

    if payments_api.is_eligible_to_physical_offers_capping(offer):
        expected_total = expenses['physical']['actual'] + requested_amount
        if expected_total > expenses['physical']['max']:
            raise exceptions.PhysicalExpenseLimitHasBeenReached(expenses['physical']['max'])

    if payments_api.is_eligible_to_digital_offers_capping(offer):
        expected_total = expenses['digital']['actual'] + requested_amount
        if expected_total > expenses['digital']['max']:
            raise exceptions.DigitalExpenseLimitHasBeenReached(expenses['digital']['max'])


def check_beneficiary_can_cancel_booking(user: UserSQLEntity, booking: Booking) -> None:
    if booking.userId != user.id:
        raise exceptions.BookingDoesntExist()
    if booking.isUsed:
        raise exceptions.BookingIsAlreadyUsed()
    if booking.isConfirmed:
        raise exceptions.CannotCancelConfirmedBooking(
            conf.BOOKING_CONFIRMATION_ERROR_CLAUSES[conf.CONFIRM_BOOKING_AFTER_CREATION_DELAY],
            conf.BOOKING_CONFIRMATION_ERROR_CLAUSES[conf.CONFIRM_BOOKING_BEFORE_EVENT_DELAY]
        )
    # TODO(fseguin, 2020-11-03: cleanup after next MEP
    if booking.stock.beginningDatetime and not booking.confirmationDate:
        if _is_confirmed(booking.stock.beginningDatetime, booking.dateCreated):
            raise exceptions.CannotCancelConfirmedBooking(
                conf.BOOKING_CONFIRMATION_ERROR_CLAUSES[conf.CONFIRM_BOOKING_AFTER_CREATION_DELAY],
                conf.BOOKING_CONFIRMATION_ERROR_CLAUSES[conf.CONFIRM_BOOKING_BEFORE_EVENT_DELAY]
            )


# FIXME: should not raise exceptions from `api_errors` (see below for details).
def check_offerer_can_cancel_booking(booking):
    if booking.isCancelled:
        gone = api_errors.ResourceGoneError()
        gone.add_error("global", "Cette contremarque a déjà été annulée")
        raise gone
    if booking.isUsed:
        forbidden = api_errors.ForbiddenError()
        forbidden.add_error('global', "Impossible d'annuler une réservation consommée")
        raise forbidden


# FIXME (dbaty, 2020-10-19): I moved this function from validation/routes/bookings.py. It
# should not raise HTTP-related exceptions. It should rather raise
# generic exceptions such as `BookingIsAlreadyUsed` and the calling
# route should have an exception handler that turns it into the
# desired HTTP-related exception (such as ResourceGone and Forbidden)
# See also functions below.
def check_is_usable(booking):
    if booking.isUsed:
        gone = api_errors.ResourceGoneError()
        gone.add_error('booking', 'Cette réservation a déjà été validée')
        raise gone
    if booking.isCancelled:
        gone = api_errors.ResourceGoneError()
        gone.add_error('booking', 'Cette réservation a été annulée')
        raise gone
    if (
            booking.stock.beginningDatetime and
            booking.stock.beginningDatetime > datetime.datetime.utcnow() + conf.USE_BOOKING_BEFORE_EVENT_DELAY
    ):
        forbidden = api_errors.ForbiddenError()
        forbidden.add_error(
            'beginningDatetime',
            "Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l'évènement",
        )
        raise forbidden


# FIXME: should not raise exceptions from `api_errors` (see above for details).
def check_is_not_activation_booking(booking: Booking) -> None:
    if user_activation.is_activation_booking(booking):
        forbidden = api_errors.ForbiddenError()
        forbidden.add_error('booking', "Impossible d'annuler une offre d'activation")
        raise forbidden


# FIXME: should not raise exceptions from `api_errors` (see above for details).
def check_can_be_mark_as_unused(booking: Booking) -> None:
    if not booking.isUsed:
        gone = api_errors.ResourceGoneError()
        gone.add_error('booking', "Cette réservation n'a pas encore été validée")
        raise gone

    if booking.isCancelled:
        gone = api_errors.ResourceGoneError()
        gone.add_error('booking', 'Cette réservation a été annulée')
        raise gone

    booking_payment = payment_queries.find_by_booking_id(booking.id)
    if booking_payment is not None:
        gone = api_errors.ResourceGoneError()
        gone.add_error('payment', "Le remboursement est en cours de traitement")
        raise gone


# TODO(fseguin, 2020-11-03): cleanup after next MEP
def _is_confirmed(event_beginning, booking_creation):
    now = datetime.datetime.utcnow()
    before_event_limit = event_beginning - conf.CONFIRM_BOOKING_BEFORE_EVENT_DELAY
    after_booking_limit = booking_creation + conf.CONFIRM_BOOKING_AFTER_CREATION_DELAY
    confirmation_date = max(min(before_event_limit, after_booking_limit), now)
    return datetime.datetime.utcnow() >= confirmation_date
