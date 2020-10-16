from typing import Dict

from flask import Request
from flask import jsonify, \
    redirect, \
    request
from flask_login import current_user, \
    login_required

from pcapi.flask_app import private_api
from pcapi.domain.build_recommendations import move_requested_recommendation_first
from pcapi.models import Recommendation
from pcapi.models.feature import FeatureToggle
from pcapi.recommendations_engine import create_recommendations_for_discovery, \
    give_requested_recommendation_to_user
from pcapi.recommendations_engine.recommendations import create_recommendations_for_discovery_v3
from pcapi.repository import feature_queries, \
    repository
from pcapi.repository.iris_venues_queries import get_iris_containing_user_location
from pcapi.repository.recommendation_queries import update_read_recommendations
from pcapi.routes.serialization.recommendation_serialize import serialize_recommendation, \
    serialize_recommendations
from pcapi.utils.config import BLOB_SIZE
from pcapi.utils.human_ids import dehumanize, \
    dehumanize_ids_list
from pcapi.utils.rest import expect_json_data

DEFAULT_PAGE = 1


@private_api.route('/recommendations/offers/<offer_id>', methods=['GET'])
@login_required
def get_recommendation(offer_id):
    recommendation = give_requested_recommendation_to_user(
        current_user,
        dehumanize(offer_id),
        dehumanize(request.args.get('mediationId'))
    )

    return jsonify(serialize_recommendation(recommendation, user_id=current_user.id)), 200


@private_api.route('/recommendations/<recommendation_id>', methods=['PATCH'])
@login_required
@expect_json_data
def patch_recommendation(recommendation_id):
    query = Recommendation.query.filter_by(id=dehumanize(recommendation_id))
    recommendation = query.first_or_404()
    recommendation.populate_from_dict(request.json)
    repository.save(recommendation)
    return jsonify(serialize_recommendation(recommendation, user_id=current_user.id)), 200


@private_api.route('/recommendations/read', methods=['PUT'])
@login_required
@expect_json_data
def put_read_recommendations():
    update_read_recommendations(request.json)

    read_recommendation_ids = [dehumanize(reco['id']) for reco in request.json]
    read_recommendations = Recommendation.query.filter(
        Recommendation.id.in_(read_recommendation_ids)
    ).all()

    return jsonify(serialize_recommendations(read_recommendations, user_id=current_user.id)), 200


@private_api.route('/recommendations/v2', methods=['PUT'])
def put_recommendations_old_v2():
    return redirect("/recommendations", code=308)


@private_api.route('/recommendations/v3', methods=['PUT'])
def put_recommendations_old_v3():
    return redirect("/recommendations", code=308)


@private_api.route('/recommendations', methods=['PUT'])
@login_required
@expect_json_data
def put_recommendations():
    if feature_queries.is_active(FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION):
        return _put_geolocated_recommendations(request)
    else:
        return _put_non_geolocated_recommendations(request)


def _put_geolocated_recommendations(request: Request) -> (Dict, int):
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    user_is_geolocated = latitude is not None and longitude is not None
    user_iris_id = get_iris_containing_user_location(latitude, longitude) if latitude and longitude else None

    update_read_recommendations(request.json.get('readRecommendations'))
    sent_offers_ids = dehumanize_ids_list(request.json.get('offersSentInLastCall'))

    recommendations = create_recommendations_for_discovery_v3(user=current_user,
                                                              user_iris_id=user_iris_id,
                                                              user_is_geolocated=user_is_geolocated,
                                                              sent_offers_ids=sent_offers_ids,
                                                              limit=BLOB_SIZE)

    return jsonify(serialize_recommendations(recommendations, user_id=current_user.id)), 200


def _put_non_geolocated_recommendations(request: Request) -> (Dict, int):
    update_read_recommendations(request.json.get('readRecommendations'))
    sent_offers_ids = dehumanize_ids_list(request.json.get('offersSentInLastCall'))

    offer_id = dehumanize(request.args.get('offerId'))
    mediation_id = dehumanize(request.args.get('mediationId'))

    requested_recommendation = give_requested_recommendation_to_user(
        current_user,
        offer_id,
        mediation_id
    )

    recommendations = create_recommendations_for_discovery(limit=BLOB_SIZE,
                                                           user=current_user,
                                                           sent_offers_ids=sent_offers_ids)

    if requested_recommendation:
        recommendations = move_requested_recommendation_first(recommendations,
                                                              requested_recommendation)

    return jsonify(serialize_recommendations(recommendations, user_id=current_user.id)), 200
