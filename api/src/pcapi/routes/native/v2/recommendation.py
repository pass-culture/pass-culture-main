from flask_login import current_user

import pcapi.connectors.recommendation as recommendation_api
import pcapi.connectors.recommendation.exceptions as reco_exc
from pcapi.core.offers import repository as offers_repo
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native import blueprint
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize

from .serialization import recommendation as serializers


@blueprint.native_route("/recommendation/similar_offers/<int:offer_id>", version="v2", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SimilarOffersResponse)
def similar_offers(
    offer_id: int,
    query: serializers.SimilarOffersRequestQuery,
) -> serializers.SimilarOffersResponse:
    user = current_user if not current_user.is_anonymous else None
    try:
        response = recommendation_api.get_similar_offers(
            offer_id,
            user,
            params=query.model_dump(mode="json"),
        )
    except reco_exc.RecommendationApiTimeoutException:
        raise ApiErrors({"code": "RECOMMENDATION_API_TIMEOUT"}, status_code=504)
    except reco_exc.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=502)

    offers = offers_repo.get_offers_by_ids(user, [int(offer_id) for offer_id in response.results]).all()

    return serializers.SimilarOffersResponse(offers=offers)


@blueprint.native_route("/recommendation/playlist", version="v2", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=serializers.PlaylistResponse)
@authenticated_and_active_user_required
def playlist(
    query: serializers.PlaylistRequestQuery,
    body: serializers.PlaylistRequestBody,
) -> serializers.PlaylistResponse:
    try:
        response = recommendation_api.get_playlist(
            current_user,
            params=query.dict(),
            body=body.dict(),
        )
    except reco_exc.RecommendationApiTimeoutException:
        raise ApiErrors({"code": "RECOMMENDATION_API_TIMEOUT"}, status_code=504)
    except reco_exc.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=502)

    offers = offers_repo.get_offers_by_ids(
        current_user,
        [int(offer_id) for offer_id in response.playlist_recommended_offers],
    ).all()

    return serializers.PlaylistResponse(offers=offers)
