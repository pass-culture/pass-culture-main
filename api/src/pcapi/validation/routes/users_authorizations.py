from pcapi.core.offerers.models import ApiKey
from pcapi.core.users.models import User
import pcapi.core.users.repository as users_repository
from pcapi.models.api_errors import ForbiddenError


def check_user_can_validate_bookings_v2(user: User, offerer_id: int) -> None:
    if not users_repository.has_access(user, offerer_id):
        api_errors = ForbiddenError()
        api_errors.add_error(
            "user",
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation",
        )
        raise api_errors


def check_api_key_allows_to_validate_booking(valid_api_key: ApiKey, offerer_id: int) -> None:
    if valid_api_key.offererId != offerer_id:
        api_errors = ForbiddenError()
        api_errors.add_error(
            "user",
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation",
        )
        raise api_errors


def check_api_key_allows_to_cancel_booking(valid_api_key: ApiKey, offerer_id: int) -> None:
    if not valid_api_key.offererId == offerer_id:
        api_errors = ForbiddenError()
        api_errors.add_error("user", "Vous n'avez pas les droits suffisants pour annuler cette réservation.")
        raise api_errors
