from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Venue
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError


def check_user_can_validate_bookings(user: User, offerer_id: int) -> bool:
    if not user.is_authenticated:
        return False

    if not user.has_access(offerer_id):
        api_errors = ApiErrors()
        api_errors.add_error("global", "Cette contremarque n'a pas été trouvée")
        raise api_errors

    return True


def check_user_can_validate_bookings_v2(user: User, offerer_id: int) -> None:
    if not user.has_access(offerer_id):
        api_errors = ForbiddenError()
        api_errors.add_error(
            "user",
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation",
        )
        raise api_errors


def check_user_can_alter_venue(user: User, venue_id: int) -> None:
    venue = Venue.query.get(venue_id)
    if not user.has_access(venue.managingOffererId):
        api_errors = ForbiddenError()
        api_errors.add_error("user", "Vous n'avez pas les droits suffisants pour modifier ce lieu.")
        raise api_errors


def check_api_key_allows_to_validate_booking(valid_api_key: ApiKey, offerer_id: int) -> None:
    if not valid_api_key.offererId == offerer_id:
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
