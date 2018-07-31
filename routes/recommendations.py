""" user mediations routes """
from datetime import datetime
from random import shuffle

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.sql.expression import func

from datascience import create_recommendation, create_recommendations
from models import Booking, Occasion
from models.api_errors import ApiErrors
from utils.human_ids import dehumanize
from utils.includes import BOOKING_INCLUDES,\
                           RECOMMENDATION_INCLUDES
from models import EventOccurrence,\
                   Mediation,\
                   Offer,\
                   PcObject,\
                   Recommendation
from utils.config import BLOB_SIZE, BLOB_READ_NUMBER, \
    BLOB_UNREAD_NUMBER
from utils.logger import logger
from utils.rest import expect_json_data


def pick_random_occasions_given_blob_size(recos, limit=BLOB_SIZE):
    return recos.order_by(func.random()) \
        .limit(limit) \
        .all()


def find_or_make_recommendation(user, occasion_id,
                                mediation_id, from_user_id=None):
    query = Recommendation.query.join(Occasion)
    logger.info('(requested) occasion_id=' + str(occasion_id)
             + ' mediation_id=' + str(mediation_id))
    if not mediation_id and not occasion_id:
        return None
    if mediation_id:
        query = query.filter(Recommendation.mediationId == mediation_id)
    if occasion_id:
        query = query.filter(Occasion.id == occasion_id)
    requested_recommendation = query.first()
    if requested_recommendation is None:
        if mediation_id:
            return None
        occasion = Occasion.query.filter_by(id=occasion_id).first()
        mediation = Mediation.query.filter_by(id=mediation_id).first()
        requested_recommendation = create_recommendation(user, occasion, mediation=mediation)

    if requested_recommendation is None:
        raise ApiErrors()

    return requested_recommendation


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
                                                           dehumanize(request.args.get('occasionId')),
                                                           dehumanize(request.args.get('mediationId')))

    if (request.args.get('occasionId')
        or request.args.get('mediationId'))\
       and requested_recommendation is None:
        return "Occasion or mediation not found", 404

    print('requested req', requested_recommendation)

    logger.info('(special) requested_recommendation '
             + str(requested_recommendation))

# TODO
#    if (request.args.get('occasionId') is not None
#        or request.args.get('mediationId') is not None)\
#       and request.args.get('singleReco') is not None\
#       and request.args.get('singleReco').lower == 'true':
#        if requested_recommendation:
#            return jsonify(dictify_recos()), 200
#        else:
#            return "", 404

    # we get more read+unread recos than needed in case we can't make enough new recos

    filter_not_seen_occasion = ~Recommendation.id.in_(seen_recommendationIds)

    query = Recommendation.query.outerjoin(Mediation)\
                                .filter((Recommendation.user == current_user)
                                        & (filter_not_seen_occasion)
                                        & (Mediation.tutoIndex == None)
                                        & ((Recommendation.validUntilDate == None)
                                           | (Recommendation.validUntilDate > datetime.utcnow())))

    filter_already_read = (Recommendation.dateRead != None)

    unread_recos = query.filter(~filter_already_read)
    unread_recos = pick_random_occasions_given_blob_size(unread_recos)

    logger.info('(unread reco) count %i', len(unread_recos))


    read_recos = query.filter(filter_already_read)
    read_recos = pick_random_occasions_given_blob_size(read_recos)

    logger.info('(read reco) count %i', len(read_recos))

    needed_new_recos = BLOB_SIZE\
                       - min(len(unread_recos), BLOB_UNREAD_NUMBER)\
                       - min(len(read_recos), BLOB_READ_NUMBER)

    logger.info('(needed new recos) count %i', needed_new_recos)

    new_recos = create_recommendations(needed_new_recos,
                                       user=current_user)

    logger.info('(new recos)'+str([(reco, reco.mediation, reco.dateRead) for reco in new_recos]))
    logger.info('(new reco) count %i', len(new_recos))

    recos = new_recos

    while len(recos) < BLOB_SIZE\
          and (len(unread_recos) > 0
               or len(read_recos) > 0):

        nb_new_unread = min(BLOB_UNREAD_NUMBER,
                            len(unread_recos),
                            BLOB_SIZE-len(recos))
        recos += unread_recos[0:nb_new_unread]
        unread_recos = unread_recos[nb_new_unread:]

        nb_new_read = min(BLOB_READ_NUMBER,
                          len(read_recos),
                          BLOB_SIZE-len(recos))
        recos += read_recos[0:nb_new_read]
        read_recos = read_recos[nb_new_read:]

    shuffle(recos)

    all_read_recos_count = Recommendation.query.filter((Recommendation.user == current_user)
                                                       & (filter_already_read))\
                                               .count()

    logger.info('(all read recos) count %i', all_read_recos_count)

    if requested_recommendation:
        for i, reco in enumerate(recos):
            if reco.id == requested_recommendation.id:
                recos = recos[:i]+recos[i+1:]
                break
        recos = [requested_recommendation] + recos
    else:
        tuto_recos = Recommendation.query.join(Mediation)\
                                   .filter((Mediation.tutoIndex != None)
                                           & (Recommendation.user == current_user)
                                           & filter_not_seen_occasion)\
                                   .order_by(Mediation.tutoIndex)\
                                   .all()
        logger.info('(tuto recos) count %i', len(tuto_recos))

        tutos_read = 0
        for tuto_reco in tuto_recos:
            if tuto_reco.dateRead is not None:
                tutos_read += 1
            elif len(recos) >= tuto_reco.mediation.tutoIndex-tutos_read:
                recos = recos[:tuto_reco.mediation.tutoIndex-tutos_read]\
                        + [tuto_reco]\
                        + recos[tuto_reco.mediation.tutoIndex-tutos_read:]

    logger.info('(recap reco) '
                + str([(reco, reco.mediation, reco.dateRead, reco.occasion) for reco in recos])
                + str(len(recos)))

    return jsonify(list(map(dictify_reco, recos))), 200


def dictify_reco(reco):

    dict_reco = reco._asdict(include=RECOMMENDATION_INCLUDES)
    if reco.occasion:
        booking_query = Booking.query\
                               .join(Offer)
        if reco.occasion.eventId:
            booking_query = booking_query.join(EventOccurrence)
        booking_query = booking_query.join(Occasion)\
                                     .filter(Booking.user == current_user)\
                                     .filter(Occasion.id == reco.occasionId)
        dict_reco['bookings'] = list(map(lambda b: b._asdict(include=BOOKING_INCLUDES),
                                         booking_query.all()))
    return dict_reco
