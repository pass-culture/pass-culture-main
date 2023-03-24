import logging

from pcapi.core.users import api as users_api
from pcapi.repository import user_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.validate import check_valid_token_for_user_validation

from . import blueprint


logger = logging.getLogger(__name__)


@blueprint.pro_private_api.route("/validate/user/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def validate_user(token: str) -> None:
    user_to_validate = user_queries.find_by_validation_token(token)
    check_valid_token_for_user_validation(user_to_validate)
    users_api.validate_pro_user_email(user_to_validate)
