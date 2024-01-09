import logging

from pcapi.core import token as token_utils
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.repository import user_queries
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


logger = logging.getLogger(__name__)


@blueprint.pro_private_api.route("/validate/user/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def validate_user(token: str) -> None:
    user_to_validate = user_queries.find_by_validation_token(token)
    if not user_to_validate:
        try:
            stored_token = token_utils.Token.load_and_check(token, token_utils.TokenType.EMAIL_VALIDATION)
            user_to_validate = users_models.User.query.get_or_404(stored_token.user_id)
            stored_token.expire()
        except users_exceptions.InvalidToken:
            errors = ResourceNotFoundError()
            errors.add_error("global", "Ce lien est invalide")
            raise errors
    users_api.validate_pro_user_email(user_to_validate)
