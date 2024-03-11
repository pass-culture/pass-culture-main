from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors


def check_user_has_access_to_offerer(user: User, offerer_id: int) -> None:
    if not user.has_access(offerer_id):
        raise ApiErrors(
            errors={
                "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."],
            },
            status_code=403,
        )
