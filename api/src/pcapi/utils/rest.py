import pcapi.core.offerers.models as offerers_models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.models import User
from pcapi.models import api_errors
from pcapi.models.api_errors import resource_not_found_error


def check_user_has_access_to_offerer(user: User, offerer_id: int) -> None:
    if not users_repository.has_access(user, offerer_id):
        raise resource_not_found_error()


def check_user_has_access_to_venues(user: User, venue_ids: list[int]) -> None:
    if not users_repository.has_access_to_venues(user, venue_ids):
        raise resource_not_found_error()


def check_venue_is_opened(venue: offerers_models.Venue) -> None:
    if venue.state == offerers_models.VenueState.CLOSED:
        raise api_errors.ForbiddenError()
