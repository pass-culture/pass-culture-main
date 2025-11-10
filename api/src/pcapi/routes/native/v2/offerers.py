from flask import abort

from pcapi.core.offerers import repository as offerers_repository
from pcapi.routes.native.v2.serialization import offerers as serializers
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


@blueprint.native_route("/venue/<int:venue_id>", version="v2", methods=["GET"])
@spectree_serialize(response_model=serializers.VenueResponse, api=blueprint.api, on_error_statuses=[404])
def get_venue_v2(venue_id: int) -> serializers.VenueResponse:
    venue = offerers_repository.get_active_venue_page_data(venue_id)
    if not venue:
        abort(404)

    return serializers.VenueResponse.model_validate(venue)
