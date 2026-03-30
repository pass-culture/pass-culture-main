from pcapi.core.users import repository as users_repository
from pcapi.core.users.models import User
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE
from pcapi.models.api_errors import ResourceNotFoundError


def check_user_has_access_to_offerer(user: User, offerer_id: int) -> None:
    if not users_repository.has_access(user, offerer_id):
        raise ResourceNotFoundError(
            errors={"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]},
        )


def check_user_has_access_to_venues(user: User, venue_ids: list[int]) -> None:
    if not users_repository.has_access_to_venues(user, venue_ids):
        raise ResourceNotFoundError(
            errors={"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]},
        )
