from functools import wraps

from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required

from pcapi.models.api_errors import ForbiddenError
from pcapi.repository.user_queries import find_user_by_email
from pcapi.utils.logger import logger


JWT_AUTH = "JWT"


def authenticated_user_required(route_function):  # type: ignore
    if not hasattr(route_function, "requires_authentication"):
        route_function.requires_authentication = []
    route_function.requires_authentication.append(JWT_AUTH)

    @wraps(route_function)
    @jwt_required
    def retrieve_authenticated_user(*args, **kwargs):  # type: ignore
        email = get_jwt_identity()
        user = find_user_by_email(email)
        if user is None or not user.isActive:
            logger.error("Authenticated user with email %s not found or inactive", email)
            raise ForbiddenError({"email": ["Utilisateur introuvable"]})

        return route_function(user, *args, **kwargs)

    return retrieve_authenticated_user
