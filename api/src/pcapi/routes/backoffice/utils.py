from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.models.api_errors import ApiErrors


def get_user_or_error(user_id: int, error_code: int = 400) -> users_models.User:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "L'utilisateur n'existe pas"}, status_code=error_code)

    return user
