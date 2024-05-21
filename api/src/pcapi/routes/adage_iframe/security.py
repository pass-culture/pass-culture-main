from functools import wraps
import logging
import typing

import flask
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError

from pcapi.core.users import utils as user_utils
from pcapi.models.api_errors import UnauthorizedError
from pcapi.routes.adage_iframe.blueprint import JWT_AUTH
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)


def adage_jwt_required(route_function: typing.Callable) -> typing.Callable:
    add_security_scheme(route_function, JWT_AUTH)

    @wraps(route_function)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:
        mandatory_authorization_type = "Bearer "
        authorization_header = flask.request.headers.get("Authorization")

        if authorization_header and mandatory_authorization_type in authorization_header:
            adage_jwt = authorization_header.replace(mandatory_authorization_type, "")
            try:
                with open(user_utils.JWT_ADAGE_PUBLIC_KEY_PATH, "rb") as reader:
                    public_key = reader.read()
                    adage_jwt_decoded = user_utils.decode_jwt_token_rs256(adage_jwt, public_key)
            except InvalidSignatureError as invalid_signature_error:
                logger.error("Signature of adage jwt cannot be verified", extra={"error": invalid_signature_error})
                raise UnauthorizedError(errors={"msg": "Unrecognized token"})
            except ExpiredSignatureError as expired_signature_error:
                logger.warning("Token has expired", extra={"error": expired_signature_error})
                raise UnauthorizedError(errors={"msg": "Token expired"})

            if not adage_jwt_decoded.get("exp"):
                logger.warning("Token does not contain an expiration date")
                raise UnauthorizedError(errors={"msg": "No expiration date provided"})

            email = adage_jwt_decoded.get("mail")
            if not email:
                logger.warning("Token does not contain an email")
                raise UnauthorizedError(errors={"Authorization": "Unrecognized token"})

            authenticated_information = AuthenticatedInformation(
                civility=adage_jwt_decoded.get("civilite"),
                lastname=adage_jwt_decoded.get("nom"),
                firstname=adage_jwt_decoded.get("prenom"),
                email=email,
                uai=adage_jwt_decoded.get("uai"),
                lat=adage_jwt_decoded.get("lat"),
                lon=adage_jwt_decoded.get("lon"),
            )
            kwargs["authenticated_information"] = authenticated_information
            return route_function(*args, **kwargs)

        raise UnauthorizedError(errors={"msg": "Unrecognized token"})

    return wrapper
