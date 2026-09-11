from flask_login import login_required

from pcapi.core.offerers import repository as offerers_repository
from pcapi.routes.pro.blueprint import pro_blueprint
from pcapi.routes.serialization.venue_labels_serialize import VenueLabelListResponseModel
from pcapi.routes.serialization.venue_labels_serialize import VenueLabelResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@pro_blueprint.route("/venue-labels", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=VenueLabelListResponseModel, api=blueprint.pro_schema)
def fetch_venue_labels() -> VenueLabelListResponseModel:
    return VenueLabelListResponseModel(
        [
            VenueLabelResponseModel.model_validate(venue_label)
            for venue_label in offerers_repository.get_all_venue_labels()
        ]
    )
