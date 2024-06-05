from pcapi.core.users import repository as users_repository
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors


def check_user_has_access_to_offerer(user: User, offerer_id: int) -> None:
    if not users_repository.has_access(user, offerer_id):
        raise ApiErrors(
            errors={
                "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."],
            },
            status_code=403,
        )
