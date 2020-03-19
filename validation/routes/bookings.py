from datetime import datetime
from typing import Callable, Dict

from domain.bookings import BOOKING_CANCELLATION_DELAY
from domain.expenses import is_eligible_to_digital_offers_capping, \
    is_eligible_to_physical_offers_capping
from domain.user_activation import is_activation_booking
from models import ApiErrors, Booking, RightsType
from models.api_errors import ResourceGoneError, ForbiddenError
from models.stock import Stock
from models.user import User
from repository import booking_queries
from repository import payment_queries, stock_queries, venue_queries
from utils.rest import ensure_current_user_has_rights


def check_has_stock_id(stock_id: int) -> None:
    if stock_id is None:
        api_errors = ApiErrors()
        api_errors.add_error('stockId', "Vous devez préciser un identifiant d'offre")
        raise api_errors


def check_quantity_is_valid(quantity: int, stock: Stock):
    offer_is_duo = stock.offer.isDuo
    is_valid_quantity_for_duo_offer = (quantity in (1, 2) and offer_is_duo)
    is_valid_quantity_for_solo_offer = (quantity == 1 and not offer_is_duo)

    if not is_valid_quantity_for_duo_offer and not is_valid_quantity_for_solo_offer:
        api_errors = ApiErrors()
        api_errors.add_error('quantity', "Vous devez réserver une place ou deux dans le cas d'une offre DUO.")
        raise api_errors


def check_existing_stock(stock: Stock) -> None:
    if stock is None:
        api_errors = ApiErrors()
        api_errors.add_error('stockId', 'stockId ne correspond à aucun stock')
        raise api_errors


def check_not_soft_deleted_stock(stock: Stock) -> None:
    if stock.isSoftDeleted:
        api_errors = ApiErrors()
        api_errors.add_error('stockId', "Cette date a été retirée. Elle n'est plus disponible.")
        raise api_errors


def check_offer_is_active(stock: Stock) -> None:
    soft_deleted_stock = stock.isSoftDeleted
    inactive_offerer = not stock.resolvedOffer.venue.managingOfferer.isActive
    inactive_offer = not stock.resolvedOffer.isActive

    if soft_deleted_stock or inactive_offerer or inactive_offer:
        api_errors = ApiErrors()
        api_errors.add_error('stockId', "Cette offre a été retirée. Elle n'est plus valable.")
        raise api_errors


def check_already_booked(stock: Stock, user: User):
    is_stock_already_booked_by_user = booking_queries.is_stock_already_booked_by_user(stock, user)
    if is_stock_already_booked_by_user:
        api_errors = ApiErrors()
        api_errors.add_error('stockId', "Cette offre a déja été reservée par l'utilisateur")
        raise api_errors


def check_stock_venue_is_validated(stock: Stock) -> None:
    if not stock.resolvedOffer.venue.isValidated:
        api_errors = ApiErrors()
        api_errors.add_error('stockId',
                             'Vous ne pouvez pas encore réserver cette offre, son lieu est en attente de validation')
        raise api_errors


def check_stock_booking_limit_date(stock: Stock) -> None:
    stock_has_expired = stock.bookingLimitDatetime is not None and stock.bookingLimitDatetime < datetime.utcnow()

    if stock_has_expired:
        api_errors = ApiErrors()
        api_errors.add_error('global', 'La date limite de réservation de cette offre est dépassée')
        raise api_errors


def check_offer_date(stock: Stock) -> None:
    stock_has_expired = stock.beginningDatetime is not None and stock.beginningDatetime < datetime.utcnow()

    if stock_has_expired:
        api_errors = ApiErrors()
        api_errors.add_error('date', "Cette offre n'est plus valable car sa date est passée")
        raise api_errors


def check_expenses_limits(expenses: Dict, booking: Booking,
                          find_stock: Callable[..., Stock] = stock_queries.find_stock_by_id) -> None:
    stock = find_stock(booking.stockId)
    offer = stock.resolvedOffer

    if is_eligible_to_physical_offers_capping(offer):
        if (expenses['physical']['actual'] + booking.value) > expenses['physical']['max']:
            raise ApiErrors(
                {'global': ['Le plafond de %s € pour les biens culturels ne vous permet pas ' \
                            'de réserver cette offre.' % expenses['physical']['max']]}
            )

    if is_eligible_to_digital_offers_capping(offer):
        if (expenses['digital']['actual'] + booking.value) > expenses['digital']['max']:
            raise ApiErrors(
                {'global': ['Le plafond de %s € pour les offres numériques ne vous permet pas ' \
                            'de réserver cette offre.' % expenses['digital']['max']]}
            )


def check_booking_token_is_usable(booking: Booking) -> None:
    resource_gone_error = ResourceGoneError()
    if booking.isUsed:
        resource_gone_error.add_error('booking', 'Cette réservation a déjà été validée')
        raise resource_gone_error
    if booking.isCancelled:
        resource_gone_error.add_error('booking', 'Cette réservation a été annulée')
        raise resource_gone_error
    event_starts_in_more_than_72_hours = booking.stock.beginningDatetime and (
            booking.stock.beginningDatetime > (datetime.utcnow() + BOOKING_CANCELLATION_DELAY))
    if event_starts_in_more_than_72_hours:
        errors = ForbiddenError()
        errors.add_error('beginningDatetime',
                         "Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l'évènement")
        raise errors


def check_booking_token_is_keepable(booking: Booking) -> None:
    resource_gone_error = ResourceGoneError()
    booking_payment = payment_queries.find_by_booking_id(booking.id)

    if booking_payment is not None:
        resource_gone_error.add_error('payment', "Le remboursement est en cours de traitement")
        raise resource_gone_error

    if not booking.isUsed:
        resource_gone_error.add_error('booking', "Cette réservation n'a pas encore été validée")
        raise resource_gone_error

    if booking.isCancelled:
        resource_gone_error.add_error('booking', 'Cette réservation a été annulée')
        raise resource_gone_error


def check_booking_is_cancellable_by_user(booking: Booking, is_user_cancellation: bool) -> None:
    api_errors = ApiErrors()

    if booking.isUsed:
        api_errors.add_error('booking', "Impossible d'annuler une réservation consommée")
        raise api_errors

    if is_user_cancellation:
        if not booking.isUserCancellable:
            api_errors.add_error('booking',
                                 "Impossible d'annuler une réservation moins de 72h avant le début de l'évènement")
            raise api_errors


def check_is_not_activation_booking(booking: Booking) -> None:
    if is_activation_booking(booking):
        error = ForbiddenError()
        error.add_error('booking', "Impossible d'annuler une offre d'activation")
        raise error


def check_email_and_offer_id_for_anonymous_user(email: str, offer_id: int) -> None:
    api_errors = ApiErrors()
    if not email:
        api_errors.add_error('email',
                             "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]")
    if not offer_id:
        api_errors.add_error('offer_id', "L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]")
    if api_errors.errors:
        raise api_errors


def check_rights_to_get_bookings_csv(user: User, venue_id: int = None, offer_id: int = None) -> None:
    if user.isAdmin:
        api_errors = ApiErrors()
        api_errors.add_error(
            'global',
            "Le statut d'administrateur ne permet pas d'accéder au suivi des réseravtions"
        )
        raise api_errors

    if venue_id:
        venue = venue_queries.find_by_id(venue_id)
        if venue is None:
            api_errors = ApiErrors()
            api_errors.add_error('venueId', "Ce lieu n'existe pas.")
            raise api_errors
        ensure_current_user_has_rights(user=user, rights=RightsType.editor, offerer_id=venue.managingOffererId)

    if offer_id:
        venue = venue_queries.find_by_offer_id(offer_id)
        if venue is None:
            api_errors = ApiErrors()
            api_errors.add_error('offerId', "Cette offre n'existe pas.")
            raise api_errors
        ensure_current_user_has_rights(user=user, rights=RightsType.editor, offerer_id=venue.managingOffererId)


def check_booking_is_not_already_cancelled(booking: Booking) -> None:
    if booking.isCancelled:
        api_errors = ResourceGoneError()
        api_errors.add_error(
            'global',
            "Cette contremarque a déjà été annulée"
        )
        raise api_errors


def check_booking_is_not_used(booking: Booking) -> None:
    if booking.isUsed:
        api_errors = ForbiddenError()
        api_errors.add_error(
            'global',
            "Impossible d'annuler une réservation consommée"
        )
        raise api_errors


def check_stock_is_bookable(stock: Stock):
    if not stock.isBookable:
        api_errors = ApiErrors()
        api_errors.add_error('stock', "Ce stock n'est pas réservable")
        raise api_errors
