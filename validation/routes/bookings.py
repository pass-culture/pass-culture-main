from datetime import datetime

from domain.bookings import BOOKING_CANCELLATION_DELAY
from domain.user_activation import is_activation_booking
from models import ApiErrors, BookingSQLEntity, RightsType
from models.api_errors import ResourceGoneError, ForbiddenError
from models.user_sql_entity import UserSQLEntity
from repository import payment_queries, venue_queries
from utils.rest import ensure_current_user_has_rights


def check_has_stock_id(stock_id: int) -> None:
    if stock_id is None:
        api_errors = ApiErrors()
        api_errors.add_error('stockId', "Vous devez préciser un identifiant d'offre")
        raise api_errors


def check_booking_token_is_usable(booking: BookingSQLEntity) -> None:
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


def check_booking_token_is_keepable(booking: BookingSQLEntity) -> None:
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


def check_booking_is_cancellable_by_user(booking: BookingSQLEntity, is_user_cancellation: bool) -> None:
    api_errors = ApiErrors()

    if booking.isUsed:
        api_errors.add_error('booking', "Impossible d'annuler une réservation consommée")
        raise api_errors

    if is_user_cancellation:
        if not booking.isUserCancellable:
            api_errors.add_error('booking',
                                 "Impossible d'annuler une réservation moins de 72h avant le début de l'évènement")
            raise api_errors


def check_is_not_activation_booking(booking: BookingSQLEntity) -> None:
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


def check_rights_to_get_bookings_csv(user: UserSQLEntity, venue_id: int = None, offer_id: int = None) -> None:
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


def check_booking_is_not_already_cancelled(booking: BookingSQLEntity) -> None:
    if booking.isCancelled:
        api_errors = ResourceGoneError()
        api_errors.add_error(
            'global',
            "Cette contremarque a déjà été annulée"
        )
        raise api_errors


def check_booking_is_not_used(booking: BookingSQLEntity) -> None:
    if booking.isUsed:
        api_errors = ForbiddenError()
        api_errors.add_error(
            'global',
            "Impossible d'annuler une réservation consommée"
        )
        raise api_errors
