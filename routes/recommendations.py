""" user mediations routes """
from datetime import datetime
from random import shuffle

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from models import Mediation, PcObject, Recommendation
from recommendations_engine import pick_random_offers_given_blob_size, create_recommendations, \
    RecommendationNotFoundException, give_requested_recommendation_to_user
from repository.booking_queries import find_bookings_from_recommendation
from repository.recommendation_queries import find_unseen_tutorials_for_user, count_read_recommendations_for_user
from utils.config import BLOB_SIZE, BLOB_READ_NUMBER, BLOB_UNREAD_NUMBER
from utils.human_ids import dehumanize
from utils.includes import BOOKING_INCLUDES, RECOMMENDATION_INCLUDES
from utils.logger import logger
from utils.rest import expect_json_data


@app.route('/recommendations/<recommendationId>', methods=['PATCH'])
@login_required
@expect_json_data
def patch_recommendation(recommendationId):
    query = Recommendation.query.filter_by(id=dehumanize(recommendationId))
    recommendation = query.first_or_404()
    recommendation.populateFromDict(request.json)
    PcObject.check_and_save(recommendation)
    return jsonify(serialize_recommendation(recommendation)), 200


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


    query = Recommendation.query.outerjoin(Mediation) \
        .filter((Recommendation.user == current_user)
                & ~Recommendation.id.in_(seen_recommendation_ids)
                & (Mediation.tutoIndex == None)
                & ((Recommendation.validUntilDate == None)
                   | (Recommendation.validUntilDate > datetime.utcnow())))

    filter_already_read = (Recommendation.dateRead != None)

    unread_recos = query.filter(~filter_already_read)
    unread_recos = pick_random_offers_given_blob_size(unread_recos)

    logger.info('(unread reco) count %i', len(unread_recos))

    read_recos = query.filter(filter_already_read)
    read_recos = pick_random_offers_given_blob_size(read_recos)

    logger.info('(read reco) count %i', len(read_recos))

    needed_new_recos = BLOB_SIZE \
                       - min(len(unread_recos), BLOB_UNREAD_NUMBER) \
                       - min(len(read_recos), BLOB_READ_NUMBER)

    logger.info('(needed new recos) count %i', needed_new_recos)

    new_recos = create_recommendations(needed_new_recos, user=current_user)

    logger.info('(new recos)' + str([(reco, reco.mediation, reco.dateRead) for reco in new_recos]))
    logger.info('(new reco) count %i', len(new_recos))

    recos = new_recos

    while len(recos) < BLOB_SIZE \
            and (len(unread_recos) > 0
                 or len(read_recos) > 0):
        nb_new_unread = min(BLOB_UNREAD_NUMBER,
                            len(unread_recos),
                            BLOB_SIZE - len(recos))
        recos += unread_recos[0:nb_new_unread]
        unread_recos = unread_recos[nb_new_unread:]

        nb_new_read = min(BLOB_READ_NUMBER,
                          len(read_recos),
                          BLOB_SIZE - len(recos))
        recos += read_recos[0:nb_new_read]
        read_recos = read_recos[nb_new_read:]

    shuffle(recos)

    all_read_recos_count = count_read_recommendations_for_user(current_user)

    logger.info('(all read recos) count %i', all_read_recos_count)

    if requested_recommendation:
        recos = move_requested_recommendation_first(recos, requested_recommendation)
    else:
        recos = move_tutorial_recommendations_first(recos, seen_recommendation_ids)

    logger.info('(recap reco) '
                + str([(reco, reco.mediation, reco.dateRead, reco.offer) for reco in recos])
                + str(len(recos)))

    return jsonify(serialize_recommendations(recos)), 200


def move_tutorial_recommendations_first(recos, seen_recommendation_ids):
    tutorial_recommendations = find_unseen_tutorials_for_user(seen_recommendation_ids, current_user)

    logger.info('(tuto recos) count %i', len(tutorial_recommendations))

    tutos_read = 0
    for reco in tutorial_recommendations:
        if reco.dateRead is not None:
            tutos_read += 1

        elif len(recos) >= reco.mediation.tutoIndex - tutos_read:
            recos = recos[:reco.mediation.tutoIndex - tutos_read] \
                    + [reco] \
                    + recos[reco.mediation.tutoIndex - tutos_read:]
    return recos


def move_requested_recommendation_first(recos, requested_recommendation):
    for i, reco in enumerate(recos):
        if reco.id == requested_recommendation.id:
            recos = recos[:i] + recos[i + 1:]
            break
    recos = [requested_recommendation] + recos
    return recos


def serialize_recommendations(recos):
    return list(map(serialize_recommendation, recos))


def serialize_recommendation(reco):
    dict_reco = reco._asdict(include=RECOMMENDATION_INCLUDES)

    if reco.offer:
        bookings = find_bookings_from_recommendation(reco, current_user)
        dict_reco['bookings'] = serialize_bookings(bookings)

    return dict_reco


def serialize_bookings(bookings):
    return list(map(serialize_booking, bookings))


def serialize_booking(booking):
    return booking._asdict(include=BOOKING_INCLUDES)
