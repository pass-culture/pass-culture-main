from flask_login import login_required

from pcapi.core.offerers import repository as offerers_repository
from pcapi.flask_app import private_api
from pcapi.routes.serialization.venue_types_serialize import VenueTypeListResponseModel
from pcapi.routes.serialization.venue_types_serialize import VenueTypeResponseModel
from pcapi.serialization.decorator import spectree_serialize


@private_api.route("/venue-types", methods=["GET"])
@login_required
@spectree_serialize(response_model=VenueTypeListResponseModel)
def get_venue_types() -> VenueTypeListResponseModel:
    venue_type_list = [
        VenueTypeResponseModel.from_orm(venue_type) for venue_type in offerers_repository.get_all_venue_types()
    ]

    return VenueTypeListResponseModel(__root__=venue_type_list)
