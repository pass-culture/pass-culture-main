import logging

import pcapi.core.reactions.api as reactions_api
import pcapi.core.users.models as users_models
from pcapi.repository import atomic
from pcapi.routes.native.security import authenticated_and_active_user_required
import pcapi.routes.native.v1.serialization.reaction as serialization
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/reaction", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
@atomic()
def post_reaction(user: users_models.User, body: serialization.PostReactionRequest) -> None:
    reactions_api.update_or_create_reaction(user.id, body.offer_id, reaction_type=body.reaction_type)
