from flask import abort

import pcapi.core.offerers.repository as offerers_repository
from pcapi.serialization.decorator import spectree_serialize

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


@blueprint.native_route("/venue/<int:venue_id>/advices", methods=["GET"])
@spectree_serialize(response_model=serializers.VenueProAdvices, api=blueprint.api, on_error_statuses=[400])
def get_venue_advices(venue_id: int, query: serializers.VenueProAdviceQuery) -> serializers.VenueProAdvices:
    offset = (query.page - 1) * query.results_per_page if query.results_per_page else 0
    pro_advices = offerers_repository.get_venue_pro_advices(venue_id, offset=offset, limit=query.results_per_page)
    if len(pro_advices) < query.results_per_page:
        nb_results = len(pro_advices)
    else:
        nb_results = offerers_repository.get_venue_pro_advices_count(venue_id)

    return serializers.VenueProAdvices(
        pro_advices=[
            serializers.VenueProAdvice.build(pro_advice, query.max_content_length) for pro_advice in pro_advices
        ],
        nb_results=nb_results,
    )
