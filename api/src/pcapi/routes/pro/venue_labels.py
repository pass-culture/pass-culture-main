from flask_login import login_required

from pcapi.core.offerers import repository as offerers_repository
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.venue_labels_serialize import VenueLabelListResponseModel
from pcapi.routes.serialization.venue_labels_serialize import VenueLabelResponseModel
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@private_api.route("/venue-labels", methods=["GET"])
@login_required
@spectree_serialize(response_model=VenueLabelListResponseModel, api=blueprint.pro_private_schema)
def fetch_venue_labels() -> VenueLabelListResponseModel:
    venue_label_list = [
        VenueLabelResponseModel.from_orm(venue_label) for venue_label in offerers_repository.get_all_venue_labels()
    ]
    return VenueLabelListResponseModel(__root__=venue_label_list)
