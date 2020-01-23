import random

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.build_recommendations import move_requested_recommendation_first, \
    move_tutorial_recommendations_first
from models import Recommendation
from recommendations_engine import create_recommendations_for_discovery, \
    create_recommendations_for_search, \
    get_recommendation_search_params, \
    give_requested_recommendation_to_user
from repository import repository
from repository.recommendation_queries import update_read_recommendations
from routes.serialization.recommendation_serialize import serialize_recommendations, serialize_recommendation
from utils.config import BLOB_SIZE
from utils.human_ids import dehumanize
from utils.logger import logger
from utils.rest import expect_json_data

DEFAULT_PAGE = 1


@app.route('/recommendations', methods=['GET'])
@login_required
def list_recommendations():
    search_params = get_recommendation_search_params(request.args)
    recommendations = create_recommendations_for_search(
        current_user,
        **search_params
    )
    return jsonify(serialize_recommendations(recommendations, current_user)), 200


@app.route('/recommendations/offers/<offer_id>', methods=['GET'])
@login_required
def get_recommendation(offer_id):
    recommendation = give_requested_recommendation_to_user(
        current_user,
        dehumanize(offer_id),
        dehumanize(request.args.get('mediationId'))
    )

    return jsonify(serialize_recommendation(recommendation, current_user)), 200


@app.route('/recommendations/<recommendation_id>', methods=['PATCH'])
@login_required
@expect_json_data
def patch_recommendation(recommendation_id):
    query = Recommendation.query.filter_by(id=dehumanize(recommendation_id))
    recommendation = query.first_or_404()
    recommendation.populate_from_dict(request.json)
    repository.save(recommendation)
    return jsonify(serialize_recommendation(recommendation, current_user)), 200


@app.route('/recommendations/read', methods=['PUT'])
@login_required
@expect_json_data
def put_read_recommendations():
    update_read_recommendations(request.json)

    read_recommendation_ids = [dehumanize(reco['id']) for reco in request.json]
    read_recommendations = Recommendation.query.filter(
        Recommendation.id.in_(read_recommendation_ids)
    ).all()

    return jsonify(serialize_recommendations(read_recommendations, current_user)), 200


@app.route('/recommendations', methods=['PUT'])
@login_required
@expect_json_data
def put_recommendations():
    json_keys = request.json.keys()

    if 'readRecommendations' in json_keys:
        update_read_recommendations(request.json['readRecommendations'] or [])

    if 'seenRecommendationIds' in json_keys:
        humanized_seen_recommendation_ids = request.json['seenRecommendationIds'] or [
        ]
        seen_recommendation_ids = list(
            map(dehumanize, humanized_seen_recommendation_ids))
    else:
        seen_recommendation_ids = []

    offer_id = dehumanize(request.args.get('offerId'))
    mediation_id = dehumanize(request.args.get('mediationId'))

    requested_recommendation = give_requested_recommendation_to_user(
        current_user,
        offer_id,
        mediation_id
    )
    logger.debug(lambda: '(special) requested_recommendation %s' %
                         requested_recommendation)

    request_page = request.args.get('page')
    request_seed = request.args.get('seed')
    pagination_params = {
        'page': DEFAULT_PAGE if request_page is None else int(request_page),
        'seed': random.random() if request_seed is None else float(request_seed)
    }

    created_recommendations = create_recommendations_for_discovery(limit=BLOB_SIZE,
                                                                   user=current_user,
                                                                   pagination_params=pagination_params)

    logger.debug(lambda: '(new recos)' + str([(reco, reco.mediation, reco.dateRead)
                                              for reco in created_recommendations]))
    logger.debug(lambda: '(new reco) count %i', len(created_recommendations))

    recommendations = move_tutorial_recommendations_first(created_recommendations,
                                                          seen_recommendation_ids,
                                                          current_user)
    if requested_recommendation:
        recommendations = move_requested_recommendation_first(created_recommendations,
                                                              requested_recommendation)

    logger.debug(lambda: '(recap reco) '
                         + str([(reco, reco.mediation, reco.dateRead, reco.offer)
                                for reco in recommendations])
                         + str(len(recommendations)))

    return jsonify(serialize_recommendations(recommendations, current_user)), 200
