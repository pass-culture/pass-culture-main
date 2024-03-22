import flask
import flask_jwt_extended

import pcapi.connectors.recommendation as recommendation_api
import pcapi.core.users.models as users_models
import pcapi.core.users.repository as users_repository
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native import blueprint
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize

from .serialization import recommendation as serializers


@blueprint.native_route("/recommendation/similar_offers/<int:offer_id>", methods=["GET"])
@spectree_serialize(api=blueprint.api, raw_response=True)
@flask_jwt_extended.jwt_required(optional=True)
def similar_offers(
    offer_id: int,
    query: serializers.SimilarOffersRequestQuery,
) -> flask.Response:
    email = flask_jwt_extended.get_jwt_identity()
    user = users_repository.find_user_by_email(email) if email else None
    try:
        raw_response = recommendation_api.get_similar_offers(
            offer_id,
            user,
            params=query.dict(),
        )
    except recommendation_api.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=400)
    return flask.Response(raw_response, mimetype="application/json")


@blueprint.native_route("/recommendation/playlist", methods=["POST"])
@spectree_serialize(api=blueprint.api, raw_response=True)
@authenticated_and_active_user_required
def playlist(
    user: users_models.User,
    query: serializers.PlaylistRequestQuery,
    body: serializers.PlaylistRequestBody,
) -> flask.Response:
    try:
        raw_response = recommendation_api.get_playlist(
            user,
            params=query.dict(),
            body=body.dict(),
        )
    except recommendation_api.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=400)
    return flask.Response(raw_response, mimetype="application/json")
