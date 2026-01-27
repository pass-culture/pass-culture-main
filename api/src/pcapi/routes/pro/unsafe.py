from flask_login import current_user
from flask_login import login_required

import pcapi.core.offerers.repository as offerers_repository
import pcapi.routes.serialization.venues_serialize as venues_serialize
from pcapi.routes.apis import private_api
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@private_api.route("/unsafe/venues", methods=["GET"])
@login_required
@spectree_serialize(response_model=venues_serialize.UnsafeVenuesResponseModel, api=blueprint.pro_private_schema)
def get_unsafe_venues() -> venues_serialize.UnsafeVenuesResponseModel:
    venue_list = offerers_repository.get_all_venues(pro_user_id=current_user.id)

    return venues_serialize.UnsafeVenuesResponseModel.from_venues(venue_list)
