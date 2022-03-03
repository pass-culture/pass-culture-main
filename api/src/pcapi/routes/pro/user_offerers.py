from flask_login import current_user
from flask_login import login_required

from pcapi.core.offerers.repository import find_user_offerers
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.offerers_serialize import ListUserOfferersResponseModel
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@private_api.route("/userOfferers/<offerer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=ListUserOfferersResponseModel, api=blueprint.pro_private_schema)
def get_user_offerer(offerer_id: str) -> ListUserOfferersResponseModel:
    user_offerers = find_user_offerers(current_user, offerer_id)
    return ListUserOfferersResponseModel(__root__=user_offerers)
