from flask import abort
from flask_login import current_user
from flask_login import login_required

from pcapi.core.users import api as users_api
from pcapi.routes.serialization.users import PatchProUserBodyModel
from pcapi.routes.serialization.users import PatchProUserResponseModel
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@blueprint.pro_private_api.route("/users/tuto-seen", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204, api=blueprint.pro_private_schema)
def patch_user_tuto_seen() -> None:
    user = current_user._get_current_object()  # get underlying User object from proxy
    users_api.set_pro_tuto_as_seen(user)


@blueprint.pro_private_api.route("/users/current", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=PatchProUserResponseModel, api=blueprint.pro_private_schema)  # type: ignore
def patch_profile(body: PatchProUserBodyModel) -> PatchProUserResponseModel:
    user = current_user._get_current_object()  # get underlying User object from proxy
    # This route should ony be used by "pro" users because it allows
    # to update different infos from `/beneficiaries/current`.
    if not user.has_pro_role and not user.has_admin_role:
        abort(400)
    attributes = body.dict()
    users_api.update_user_info(user, **attributes)
    return PatchProUserResponseModel.from_orm(user)
