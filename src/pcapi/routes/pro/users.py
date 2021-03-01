from flask_login import current_user

from pcapi.core.users.api import set_pro_tuto_as_seen
from pcapi.core.users.models import User
from pcapi.flask_app import private_api
from pcapi.models import ApiErrors
from pcapi.routes.serialization.users import PatchUserBodyModel
from pcapi.routes.serialization.users import PatchUserResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.use_cases.update_user_informations import AlterableUserInformations
from pcapi.use_cases.update_user_informations import update_user_informations
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import expect_json_data
from pcapi.utils.rest import load_or_404
from pcapi.utils.rest import login_or_api_key_required


@private_api.route("/users/<user_id>/tuto-seen", methods=["PATCH"])
@login_or_api_key_required
@spectree_serialize(response_model=None, on_success_status=204)
def patch_user_tuto_seen(user_id: str) -> None:
    user = load_or_404(User, user_id)
    _ensure_current_user_has_rights(user_id)
    set_pro_tuto_as_seen(user)


@private_api.route("/users/current", methods=["PATCH"])
@login_or_api_key_required
@expect_json_data
@spectree_serialize(response_model=PatchUserResponseModel)  # type: ignore
def patch_profile(body: PatchUserBodyModel) -> PatchUserResponseModel:
    user_informations = AlterableUserInformations(user_id=current_user.id, **body.dict())
    user = update_user_informations(user_informations)
    response_user_model = PatchUserResponseModel.from_orm(user)

    return response_user_model


def _ensure_current_user_has_rights(user_id):
    if current_user.id != dehumanize(user_id):
        errors = ApiErrors()
        errors.add_error("global", "Vous n'avez pas les droits d'accès suffisant pour effectuer cette modificaiton.")
        errors.status_code = 403
        raise errors
