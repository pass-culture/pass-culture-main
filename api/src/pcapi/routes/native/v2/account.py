from pcapi.core.users import email as email_api
from pcapi.core.users import exceptions
from pcapi.core.users import models as users_models
from pcapi.repository import atomic
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.api_errors import account as account_errors
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


@blueprint.native_route("/profile/update_email", version="v2", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def update_user_email(user: users_models.User) -> None:
    try:
        email_api.request_email_update(user)
    except exceptions.EmailUpdateTokenExists:
        raise account_errors.EmailUpdatePendingError()
    except exceptions.EmailUpdateLimitReached:
        raise account_errors.EmailUpdateLimitError()
