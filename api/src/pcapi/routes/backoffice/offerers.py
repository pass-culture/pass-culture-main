from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from . import serialization


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/users", methods=["GET"])
@spectree_serialize(
    response_model=serialization.OffererAttachedUsersResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_OFFERER)
def get_offerer_users(offerer_id: int) -> serialization.OffererAttachedUsersResponseModel:
    """Get the list of all (pro) users attached to the offerer"""
    users_offerer: list[offerers_models.UserOfferer] = (
        offerers_models.UserOfferer.query.filter(
            offerers_models.UserOfferer.offererId == offerer_id, offerers_models.UserOfferer.isValidated
        )
        .order_by(offerers_models.UserOfferer.id)
        .all()
    )

    return serialization.OffererAttachedUsersResponseModel(
        data=[serialization.OffererAttachedUser.from_orm(user_offerer.user) for user_offerer in users_offerer]
    )
