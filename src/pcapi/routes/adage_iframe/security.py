from functools import wraps
import logging

from flask import request
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError
from jwt import InvalidTokenError

from pcapi.core.users import utils as user_utils
from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.adage_iframe.blueprint import JWT_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)


def adage_jwt_required(route_function):
    add_security_scheme(route_function, JWT_AUTH)

    @wraps(route_function)
    def wrapper(*args, **kwargs):
        mandatory_authorization_type = "Bearer "
        authorization_header = request.headers.get("Authorization")

        if authorization_header and mandatory_authorization_type in authorization_header:
            adage_jwt = authorization_header.replace(mandatory_authorization_type, "")
            try:
                adage_jwt_decoded = user_utils.decode_jwt_token_rs256(adage_jwt)
            except InvalidSignatureError as invalid_signature_error:
                logger.error("Signature of adage jwt cannot be verified", extra={"error": invalid_signature_error})
                raise ForbiddenError({"Authorization": "Unrecognized token"})
            except ExpiredSignatureError as expired_signature_error:
                logger.warning("Token has expired", extra={"error": expired_signature_error})
                raise InvalidTokenError({"Token expired"})

            if not adage_jwt_decoded.get("exp"):
                logger.warning("Token does not contain an expiration date")
                raise InvalidTokenError("No expiration date provided")

            kwargs["authenticated_email"] = adage_jwt_decoded.get("email")
            return route_function(*args, **kwargs)

        raise ForbiddenError({"Authorization": ["Unrecognized token"]})

    return wrapper
