from models import ApiErrors, RightsType, ApiKey
from models.api_errors import ForbiddenError


def check_user_can_validate_bookings(self, offerer_id: int):
    if self.is_authenticated:
        if self.hasRights(RightsType.editor, offerer_id):
            return True
        else:
            api_errors = ApiErrors()
            api_errors.add_error('global', 'Cette contremarque n\'a pas été trouvée')
            raise api_errors
    else:
        return False


def check_user_can_validate_bookings_v2(self, offerer_id: int):
    user_has_editors_right = self.hasRights(RightsType.editor, offerer_id)
    if not user_has_editors_right:
        api_errors = ForbiddenError()
        api_errors.add_error('user', 'Vous n\'avez pas les droits suffisants pour valider cette contremarque.')
        raise api_errors


def check_api_key_allows_to_validate_booking(valid_api_key: ApiKey, offerer_id: int):
    if not valid_api_key.offererId == offerer_id:
        api_errors = ForbiddenError()
        api_errors.add_error(
            'user',
            'Vous n\'avez pas les droits suffisants pour valider cette contremarque.'
        )
        raise api_errors


def check_api_key_allows_to_cancel_booking(valid_api_key: ApiKey, offerer_id: int):
    if not valid_api_key.offererId == offerer_id:
        api_errors = ForbiddenError()
        api_errors.add_error('user', 'Vous n\'avez pas les droits suffisants pour annuler cette réservation.')
        raise api_errors


def check_user_can_validate_activation_offer(user):
    forbidden_error = ForbiddenError()
    if not user.isAdmin:
        forbidden_error.add_error(
            'user',
            "Vous n'avez pas les droits suffisants pour valider cette contremarque."
        )
        raise forbidden_error


def check_can_book_free_offer(stock, user):
    if not user.canBookFreeOffers and stock.price == 0:
        api_errors = ApiErrors()
        api_errors.add_error('cannotBookFreeOffers', 'Votre compte ne vous permet pas de faire de réservation.')
        raise api_errors


def check_user_can_cancel_booking_by_id(is_user_cancellation, is_offerer_cancellation):
    forbidden_error = ForbiddenError()
    if not is_user_cancellation and not is_offerer_cancellation:
        forbidden_error.add_error(
            'user',
            "Vous n'avez pas les droits suffisants pour annuler cette réservation."
        )
        raise forbidden_error
