import pcapi.core.users.repository as users_repository
from pcapi.core.users.models import User
from pcapi.models.api_errors import ResourceNotFoundError


TOKEN_NOT_FOUND_ERROR_MESSAGE = (
    "La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder."
)


def check_user_can_validate_bookings_v2(user: User, offerer_id: int) -> None:
    if not users_repository.has_access(user, offerer_id):
        api_errors = ResourceNotFoundError()
        api_errors.add_error(
            "global",  # purposefully generic field name to avoid leaking info
            TOKEN_NOT_FOUND_ERROR_MESSAGE,
        )
        raise api_errors
