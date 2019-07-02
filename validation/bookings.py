from datetime import datetime

from domain.expenses import is_eligible_to_physical_products_capping, is_eligible_to_digital_products_capping
from domain.bookings import BOOKING_CANCELLATION_DELAY
from models import ApiErrors, Booking, RightsType
from models.api_errors import ResourceGoneError, ForbiddenError
from repository.stock_queries import find_stock_by_id
from utils.rest import ensure_current_user_has_rights
from repository.venue_queries import find_by_id
from repository.offerer_queries import get_by_offer_id, get_by_venue_id_and_offer_id


def check_has_stock_id(stock_id):
    if stock_id is None:
        api_errors = ApiErrors()
        api_errors.addError('stockId', 'Vous devez préciser un identifiant d\'offre')
        raise api_errors


def check_has_quantity(quantity):
    if quantity is None or quantity <= 0:
        api_errors = ApiErrors()
        api_errors.addError('quantity', 'Vous devez préciser une quantité pour la réservation')
        raise api_errors


def check_booking_quantity_limit(quantity):
    if quantity > 1:
        api_errors = ApiErrors()
        api_errors.addError('quantity', "Vous ne pouvez pas réserver plus d'une offre à la fois")
        raise api_errors


def check_existing_stock(stock):
    if stock is None:
        api_errors = ApiErrors()
        api_errors.addError('stockId', 'stockId ne correspond à aucun stock')
        raise api_errors


def check_not_soft_deleted_stock(stock):
    if stock.isSoftDeleted:
        api_errors = ApiErrors()
        api_errors.addError('stockId', "Cette date a été retirée. Elle n'est plus disponible.")
        raise api_errors


def check_can_book_free_offer(stock, user):
    if not user.canBookFreeOffers and stock.price == 0:
        api_errors = ApiErrors()
        api_errors.addError('cannotBookFreeOffers', 'Votre compte ne vous permet pas de faire de réservation.')
        raise api_errors


def check_offer_is_active(stock):
    soft_deleted_stock = stock.isSoftDeleted
    inactive_offerer = not stock.resolvedOffer.venue.managingOfferer.isActive
    inactive_offer = not stock.resolvedOffer.isActive

    if soft_deleted_stock or inactive_offerer or inactive_offer:
        api_errors = ApiErrors()
        api_errors.addError('stockId', "Cette offre a été retirée. Elle n'est plus valable.")
        raise api_errors


def check_already_booked(user_bookings):
    already_booked = len(user_bookings) > 0
    if already_booked:
        api_errors = ApiErrors()
        api_errors.addError('stockId', "Cette offre a déja été reservée par l'utilisateur")
        raise api_errors


def check_stock_venue_is_validated(stock):
    if not stock.resolvedOffer.venue.isValidated:
        api_errors = ApiErrors()
        api_errors.addError('stockId',
                            'Vous ne pouvez pas encore réserver cette offre, son lieu est en attente de validation')
        raise api_errors


def check_stock_booking_limit_date(stock):
    stock_has_expired = stock.bookingLimitDatetime is not None and stock.bookingLimitDatetime < datetime.utcnow()

    if stock_has_expired:
        api_errors = ApiErrors()
        api_errors.addError('global', 'La date limite de réservation de cette offre est dépassée')
        raise api_errors


def check_offer_date(stock):
    stock_has_expired = stock.beginningDatetime is not None and stock.beginningDatetime < datetime.utcnow()

    if stock_has_expired:
        api_errors = ApiErrors()
        api_errors.addError('date', "Cette offre n'est plus valable car sa date est passée")
        raise api_errors


def check_expenses_limits(expenses: dict, booking: Booking, find_stock=find_stock_by_id):
    stock = find_stock(booking.stockId)
    product = stock.resolvedOffer.product

    if is_eligible_to_physical_products_capping(product):
        if (expenses['physical']['actual'] + booking.value) > expenses['physical']['max']:
            raise ApiErrors(
                {'global': ['La limite de %s € pour les biens culturels ne vous permet pas ' \
                            'de réserver' % expenses['physical']['max']]}
            )

    if is_eligible_to_digital_products_capping(product):
        if (expenses['digital']['actual'] + booking.value) > expenses['digital']['max']:
            raise ApiErrors(
                {'global': ['La limite de %s € pour les offres numériques ne vous permet pas ' \
                            'de réserver' % expenses['digital']['max']]}
            )


def check_user_is_logged_in_or_email_is_provided(user, email):
    if not (user.is_authenticated or email):
        api_errors = ApiErrors()
        api_errors.addError('email',
                            'Vous devez préciser l\'email de l\'utilisateur quand vous n\'êtes pas connecté(e)')
        raise api_errors


def check_booking_is_usable(booking: Booking):
    resource_gone_error = ResourceGoneError()
    if booking.isUsed:
        resource_gone_error.addError('booking', 'Cette réservation a déjà été validée')
        raise resource_gone_error
    if booking.isCancelled:
        resource_gone_error.addError('booking', 'Cette réservation a été annulée')
        raise resource_gone_error
    event_starts_in_more_than_72_hours = booking.stock.beginningDatetime and (
            booking.stock.beginningDatetime > (datetime.utcnow() + BOOKING_CANCELLATION_DELAY))
    if event_starts_in_more_than_72_hours:
        errors = ForbiddenError()
        errors.addError('beginningDatetime',
                        'Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l\'évènement')
        raise errors


def check_booking_is_cancellable(booking, is_user_cancellation):
    api_errors = ApiErrors()

    if booking.isUsed:
        api_errors.addError('booking', "Impossible d\'annuler une réservation consommée")
        raise api_errors

    if is_user_cancellation:
        if not booking.isUserCancellable:
            api_errors.addError('booking',
                                "Impossible d\'annuler une réservation moins de 72h avant le début de l'évènement")
            raise api_errors


def check_email_and_offer_id_for_anonymous_user(email, offer_id):
    api_errors = ApiErrors()
    if not email:
        api_errors.addError('email',
                            "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]")
    if not offer_id:
        api_errors.addError('offer_id', "L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]")
    if api_errors.errors:
        raise api_errors


def check_rights_for_activation_offer(user):
    if not user.isAdmin:
        raise ForbiddenError


def check_rights_to_get_bookings_csv(user, venue_id):
    if venue_id:
        venue = find_by_id(venue_id)
        ensure_current_user_has_rights(user=user, rights=RightsType.editor, offerer_id=venue.managingOffererId)
