from flask_login import login_required

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.venue_types_serialize import VenueTypeListResponseModel
from pcapi.routes.serialization.venue_types_serialize import VenueTypeResponseModelV2
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@private_api.route("/venue-types", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=VenueTypeListResponseModel, api=blueprint.pro_private_schema)
def get_venue_types() -> VenueTypeListResponseModel:
    return VenueTypeListResponseModel(
        [
            VenueTypeResponseModelV2(value=venue_type.name, label=venue_type.value)
            for venue_type in offerers_models.VenueTypeCode
        ]
    )
