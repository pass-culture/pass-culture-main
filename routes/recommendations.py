""" user mediations routes """
from datetime import datetime
from random import shuffle

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from models import Booking, Offer
from models import EventOccurrence, Mediation, Stock, PcObject, Recommendation
from recommendations_engine.recommendations import pick_random_offers_given_blob_size, find_or_make_recommendation, \
    create_recommendations
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
    return jsonify(dictify_reco(recommendation)), 200


@app.route('/recommendations', methods=['PUT'])
@login_required
@expect_json_data
def put_recommendations():
    if 'seenRecommendationIds' in request.json.keys():
        humanized_seen_recommendationIds = request.json['seenRecommendationIds'] or []
        seen_recommendationIds = list(map(dehumanize, humanized_seen_recommendationIds))
    else:
        seen_recommendationIds = []
    requested_recommendation = find_or_make_recommendation(current_user,
                                                           dehumanize(request.args.get('offerId')),
                                                           dehumanize(request.args.get('mediationId')))

    if (request.args.get('offerId')
        or request.args.get('mediationId')) \
            and requested_recommendation is None:
        return "Offer or mediation not found", 404

    print('requested req', requested_recommendation)

    logger.info('(special) requested_recommendation '
                + str(requested_recommendation))

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

    filter_not_seen_offer = ~Recommendation.id.in_(seen_recommendationIds)

    query = Recommendation.query.outerjoin(Mediation) \
        .filter((Recommendation.user == current_user)
                & (filter_not_seen_offer)
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

    new_recos = create_recommendations(needed_new_recos,
                                       user=current_user)

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

    all_read_recos_count = Recommendation.query.filter((Recommendation.user == current_user)
                                                       & (filter_already_read)) \
        .count()

    logger.info('(all read recos) count %i', all_read_recos_count)

    if requested_recommendation:
        for i, reco in enumerate(recos):
            if reco.id == requested_recommendation.id:
                recos = recos[:i] + recos[i + 1:]
                break
        recos = [requested_recommendation] + recos
    else:
        tuto_recos = Recommendation.query.join(Mediation) \
            .filter((Mediation.tutoIndex != None)
                    & (Recommendation.user == current_user)
                    & filter_not_seen_offer) \
            .order_by(Mediation.tutoIndex) \
            .all()
        logger.info('(tuto recos) count %i', len(tuto_recos))

        tutos_read = 0
        for tuto_reco in tuto_recos:
            if tuto_reco.dateRead is not None:
                tutos_read += 1
            elif len(recos) >= tuto_reco.mediation.tutoIndex - tutos_read:
                recos = recos[:tuto_reco.mediation.tutoIndex - tutos_read] \
                        + [tuto_reco] \
                        + recos[tuto_reco.mediation.tutoIndex - tutos_read:]

    logger.info('(recap reco) '
                + str([(reco, reco.mediation, reco.dateRead, reco.offer) for reco in recos])
                + str(len(recos)))

    return jsonify(list(map(dictify_reco, recos))), 200


def dictify_reco(reco):
    dict_reco = reco._asdict(include=RECOMMENDATION_INCLUDES)
    if reco.offer:
        booking_query = Booking.query \
            .join(Stock)
        if reco.offer.eventId:
            booking_query = booking_query.join(EventOccurrence)
        booking_query = booking_query.join(Offer) \
            .filter(Booking.user == current_user) \
            .filter(Offer.id == reco.offerId)
        dict_reco['bookings'] = list(map(lambda b: b._asdict(include=BOOKING_INCLUDES),
                                         booking_query.all()))
    return dict_reco
