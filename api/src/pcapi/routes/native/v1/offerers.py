import sqlalchemy.orm as sa_orm
from flask import abort

import pcapi.core.offerers.repository as offerers_repository
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import offerers as serializers


# It will break the WebApp v2 proxy in case of endpoint modification. Read https://github.com/pass-culture/pass-culture-app-native/pull/2808/files#r844891000
@blueprint.native_route("/venue/<int:venue_id>", methods=["GET"])
@spectree_serialize(
    response_model=serializers.VenueResponse, api=blueprint.api, on_error_statuses=[404], deprecated=True
)
def get_venue(venue_id: int) -> serializers.VenueResponse:
    venue = offerers_repository.find_venue_by_id_with_address(venue_id)
    if not venue or not venue.isPermanent or venue.managingOfferer.isClosed or not venue.managingOfferer.isActive:
        abort(404)

    return serializers.VenueResponse.from_orm(venue)


@blueprint.native_route("/offerer/<int:offerer_id>/headline-offer", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=serializers.OffererHeadLineOfferResponseModel, api=blueprint.api, on_error_statuses=[404]
)
def get_offerer_headline_offer(
    offerer_id: int,
) -> serializers.OffererHeadLineOfferResponseModel:
    try:
        offerer_headline_offer = offerers_repository.get_offerer_headline_offer(offerer_id)
    except sa_orm.exc.NoResultFound:
        abort(404)

    return serializers.OffererHeadLineOfferResponseModel.from_orm(offerer_headline_offer)
