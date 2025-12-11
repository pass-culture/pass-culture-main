from flask_login import current_user

import pcapi.connectors.recommendation as recommendation_api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native import blueprint
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize

from .serialization import recommendation as serializers


@blueprint.native_route("/recommendation/similar_offers/<int:offer_id>", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SimilarOffersResponse)
def similar_offers(
    offer_id: int,
    query: serializers.SimilarOffersRequestQuery,
) -> serializers.SimilarOffersResponse:
    user = current_user if not current_user.is_anonymous else None
    try:
        raw_response = recommendation_api.get_similar_offers(
            offer_id,
            user,
            params=query.dict(),
        )
    except recommendation_api.RecommendationApiTimeoutException:
        raise ApiErrors({"code": "RECOMMENDATION_API_TIMEOUT"}, status_code=504)
    except recommendation_api.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=502)
    if not raw_response:
        return serializers.SimilarOffersResponse(results=[], params=serializers.RecommendationApiParams())
    return serializers.SimilarOffersResponse.parse_raw(raw_response, content_type="application/json")


@blueprint.native_route("/recommendation/playlist", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=serializers.PlaylistResponse)
@authenticated_and_active_user_required
def playlist(
    query: serializers.PlaylistRequestQuery,
    body: serializers.PlaylistRequestBody,
) -> serializers.PlaylistResponse:
    try:
        raw_response = recommendation_api.get_playlist(
            current_user,
            params=query.dict(),
            body=body.dict(),
        )
    except recommendation_api.RecommendationApiTimeoutException:
        raise ApiErrors({"code": "RECOMMENDATION_API_TIMEOUT"}, status_code=504)
    except recommendation_api.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=502)

    if not raw_response:
        return serializers.PlaylistResponse(
            playlist_recommended_offers=[], params=serializers.RecommendationApiParams()
        )
    return serializers.PlaylistResponse.parse_raw(raw_response, content_type="application/json")
