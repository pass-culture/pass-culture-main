""" user mediations routes """
from random import shuffle
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.build_recommendations import build_mixed_recommendations,\
                                         move_requested_recommendation_first,\
                                         move_tutorial_recommendations_first
from models import Booking,\
                   Event,\
                   EventOccurrence,\
                   Mediation,\
                   Offer,\
                   PcObject,\
                   Recommendation,\
                   Thing,\
                   Venue
from recommendations_engine import create_recommendations,\
                                   give_requested_recommendation_to_user,\
                                   move_requested_recommendation_first,\
                                   move_tutorial_recommendations_first,\
                                   pick_random_offers_given_blob_size,\
                                   RecommendationNotFoundException
from repository.booking_queries import find_bookings_from_recommendation
from repository.recommendation_queries import count_read_recommendations_for_user, \
                                              find_all_unread_recommendations, \
                                              find_all_read_recommendations,\
                                              give_requested_recommendation_to_user
from recommendations_engine import create_recommendations_for_discovery,\
                                   create_recommendations_for_search,\
                                   give_requested_recommendation_to_user,\
                                   RecommendationNotFoundException
from repository.booking_queries import find_bookings_from_recommendation
from repository.recommendation_queries import find_all_read_recommendations
from utils.config import BLOB_SIZE, BLOB_READ_NUMBER, BLOB_UNREAD_NUMBER
from utils.human_ids import dehumanize
from utils.includes import BOOKING_INCLUDES, RECOMMENDATION_INCLUDES
from utils.logger import logger
from utils.rest import expect_json_data,\
                       handle_rest_get_list
from utils.search import get_search_filter,\
                         handle_rest_get_list,\
                         login_or_api_key_required

@app.route('/recommendations', methods=['GET'])
@login_or_api_key_required
def list_recommendations():

    recommendations = create_recommendations_for_search(
        request.args.get('page'),
        current_user,
        request.args.get('search')
    )

    return jsonify(_serialize_recommendations(recommendations)), 200

@app.route('/recommendations/<recommendationId>', methods=['PATCH'])
@login_required
@expect_json_data
def patch_recommendation(recommendationId):
    query = Recommendation.query.filter_by(id=dehumanize(recommendationId))
    recommendation = query.first_or_404()
    recommendation.populateFromDict(request.json)
    PcObject.check_and_save(recommendation)
    return jsonify(_serialize_recommendation(recommendation)), 200


@app.route('/recommendations', methods=['PUT'])
@login_required
@expect_json_data
def put_recommendations():
    if 'seenRecommendationIds' in request.json.keys():
        humanized_seen_recommendation_ids = request.json['seenRecommendationIds'] or []
        seen_recommendation_ids = list(map(dehumanize, humanized_seen_recommendation_ids))
    else:
        seen_recommendation_ids = []

    offer_id = dehumanize(request.args.get('offerId'))
    mediation_id = dehumanize(request.args.get('mediationId'))

    try:
        requested_recommendation = give_requested_recommendation_to_user(current_user, offer_id, mediation_id)
    except RecommendationNotFoundException:
        return "Offer or mediation not found", 404

    logger.info('(special) requested_recommendation %s' % (requested_recommendation,))

    # TODO
    #    if (request.args.get('offerId') is not None
    #        or request.args.get('mediationId') is not None)\
    #       and request.args.get('singleReco') is not None\
    #       and request.args.get('singleReco').lower == 'true':
    #        if requested_recommendation:
    #            return jsonify(dictify_recos()), 200
    #        else:
    #            return "", 404

    # we get more read+unread recos than needed in case we can't make enough new recos

    unread_recos = find_all_unread_recommendations(current_user, seen_recommendation_ids)
    read_recos = find_all_read_recommendations(current_user, seen_recommendation_ids)


    needed_new_recos = BLOB_SIZE \
                       - min(len(unread_recos), BLOB_UNREAD_NUMBER) \
                       - min(len(read_recos), BLOB_READ_NUMBER)

    created_recommendations = create_recommendations_for_discovery(needed_new_recos, user=current_user)

    logger.info('(unread reco) count %i', len(unread_recos))
    logger.info('(read reco) count %i', len(read_recos))
    logger.info('(needed new recos) count %i', needed_new_recos)
    logger.info('(new recos)' + str([(reco, reco.mediation, reco.dateRead) for reco in created_recommendations]))
    logger.info('(new reco) count %i', len(created_recommendations))

    recommendations = build_mixed_recommendations(created_recommendations, read_recos, unread_recos)

    shuffle(recommendations)

    all_read_recos_count = count_read_recommendations_for_user(current_user)

    logger.info('(all read recos) count %i', all_read_recos_count)

    if requested_recommendation:
        recommendations = move_requested_recommendation_first(recommendations, requested_recommendation)
    else:
        recommendations = move_tutorial_recommendations_first(recommendations, seen_recommendation_ids, current_user)

    logger.info('(recap reco) '
                + str([(reco, reco.mediation, reco.dateRead, reco.offer) for reco in recommendations])
                + str(len(recommendations)))

    return jsonify(_serialize_recommendations(recommendations)), 200


def _serialize_recommendations(recos):
    return list(map(_serialize_recommendation, recos))


def _serialize_recommendation(reco):
    dict_reco = reco._asdict(include=RECOMMENDATION_INCLUDES)

    if reco.offer:
        bookings = find_bookings_from_recommendation(reco, current_user)
        dict_reco['bookings'] = _serialize_bookings(bookings)

    return dict_reco


def _serialize_bookings(bookings):
    return list(map(_serialize_booking, bookings))


def _serialize_booking(booking):
    return booking._asdict(include=BOOKING_INCLUDES)
