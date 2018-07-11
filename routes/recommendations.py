""" user mediations routes """
from datetime import datetime
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from random import shuffle
from sqlalchemy import update
from sqlalchemy.sql.expression import func

from datascience import create_recommendation, create_recommendations
from models.api_errors import ApiErrors
from utils.rest import expect_json_data
from utils.config import BLOB_SIZE, BLOB_READ_NUMBER,\
                         BLOB_UNREAD_NUMBER
from utils.human_ids import dehumanize, humanize
from utils.includes import RECOMMENDATION_INCLUDES,\
                           RECOMMENDATION_OFFER_INCLUDES
from utils.rest import expect_json_data,\
                       update

Event = app.model.Event
Mediation = app.model.Mediation
Offer = app.model.Offer
Recommendation = app.model.Recommendation
Thing = app.model.Thing

log = app.log


def pick_random_occasions_given_blob_size(recos, limit=BLOB_SIZE):
    return recos.order_by(func.random()) \
        .limit(limit) \
        .all()


def find_or_make_recommendation(user, occasion_type, occasion_id,
                                mediation_id, from_user_id=None):
    if isinstance(occasion_type, str):
        occasion_type = occasion_type.lower()
    query = Recommendation.query
    log.info('(special) occasion_id=' + str(occasion_id)
             + ' mediation_id=' + str(mediation_id))
    if not mediation_id and not (occasion_id and occasion_type):
        return None
    if mediation_id:
        filter = (Recommendation.mediationId == mediation_id)
    elif occasion_id and occasion_type:
        if occasion_type == 'thing':
            filter = (Recommendation.thingId == occasion_id)
        elif occasion_type == 'event':
            filter = (Recommendation.eventId == occasion_id)
        else:
            ae = ApiErrors()
            ae.addError('occasion_type',
                        "Invalid occasion type : "+occasion_type)
            raise ae
    requested_recommendation = query.filter(filter & (Recommendation.userId==user.id))\
                                    .first()
    if requested_recommendation is None:
        if mediation_id:
            return None
        elif occasion_type == 'thing':
            occasion = Thing.query.filter_by(id=occasion_id).first()
        elif occasion_type == 'event':
            occasion = Event.query.filter_by(id=occasion_id).first()
        mediation = Mediation.query.filter_by(id=mediation_id).first()
        requested_recommendation = create_recommendation(user, occasion, mediation=mediation)

    return requested_recommendation


@app.route('/recommendations/<recommendationId>', methods=['PATCH'])
@login_required
@expect_json_data
def patch_recommendation(recommendationId):
    query = Recommendation.query.filter_by(id=dehumanize(recommendationId))
    recommendation = query.first_or_404()
    update(recommendation, request.json)
    app.model.PcObject.check_and_save(recommendation)
    return jsonify(recommendation._asdict()), 200




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
                                                           request.args.get('occasionType'),
                                                           dehumanize(request.args.get('occasionId')),
                                                           dehumanize(request.args.get('mediationId')))

    print('requested req', requested_recommendation)

    log.info('(special) requested_recommendation '
             + str(requested_recommendation))

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

    log.info('(unread reco) count %i', len(unread_recos))


    read_recos = query.filter(filter_already_read)
    read_recos = pick_random_occasions_given_blob_size(read_recos)

    log.info('(read reco) count %i', len(read_recos))

    needed_new_recos = BLOB_SIZE\
                       - min(len(unread_recos), BLOB_UNREAD_NUMBER)\
                       - min(len(read_recos), BLOB_READ_NUMBER)

    log.info('(needed new recos) count %i', needed_new_recos)

    new_recos = create_recommendations(needed_new_recos,
                                       user=current_user)

    log.info('(new recos)'+str([(reco, reco.mediation, reco.dateRead) for reco in new_recos]))
    log.info('(new reco) count %i', len(new_recos))

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

    log.info('(all read recos) count %i', all_read_recos_count)

    if requested_recommendation:
        for i, reco in enumerate(recos):
            if reco.id == requested_recommendation.id:
                recos = recos[:i]+recos[i+1:]
                break
        recos = [requested_recommendation] + recos
    elif request.args.get('occasionId') is None\
         and request.args.get('mediationId') is None:
        tuto_recos = Recommendation.query.join(Mediation)\
                                   .filter((Mediation.tutoIndex != None)
                                           & (Recommendation.user == current_user)
                                           & filter_not_seen_occasion)\
                                   .order_by(Mediation.tutoIndex)\
                                   .all()
        log.info('(tuto recos) count %i', len(tuto_recos))

        tutos_read = 0
        for tuto_reco in tuto_recos:
            if tuto_reco.dateRead is not None:
                tutos_read += 1
            elif len(recos) >= tuto_reco.mediation.tutoIndex-tutos_read:
                recos = recos[:tuto_reco.mediation.tutoIndex-tutos_read]\
                        + [tuto_reco]\
                        + recos[tuto_reco.mediation.tutoIndex-tutos_read:]

    log.info('(recap reco) '
             + str([(reco, reco.mediation, reco.dateRead, reco.thing, reco.event) for reco in recos])
             + str(len(recos)))

    return jsonify(dictify_recos(recos)), 200


def dictify_recos(recos):
    # FIXME: This is to support legacy code in the webapp
    # it should be removed once all requests from the webapp
    # have an app version header, which will mean that all
    # clients (or at least those who do use the app) have
    # a recent version of the app

    dict_recos = list(map(lambda r: r._asdict(include=RECOMMENDATION_INCLUDES),
                          recos))

    for index, reco in enumerate(dict_recos):
        rbs = []
        for b in recos[index].bookings:
            rb = {}
            rb['booking'] = b
            rbs.append(rb)
        reco['recommendationBookings'] = rbs

        if recos[index].event is not None or\
           (recos[index].mediation is not None and
            recos[index].mediation.event is not None):
            if recos[index].event is not None:
                occurences = recos[index].event.occurences
            else:
                occurences = recos[index].mediation.event.occurences
            ros = list(map(lambda eo: eo.offers[0]._asdict(include=RECOMMENDATION_OFFER_INCLUDES),
                           filter(lambda eo: len(eo.offers) > 0,
                                  occurences)))
            reco['recommendationOffers'] = sorted(ros,
                                                  key=lambda ro: ro['bookingLimitDatetime'],
                                                  reverse=True)
        elif recos[index].mediation and\
             recos[index].mediation.tutoIndex is not None:
            reco['recommendationOffers'] = []

    return dict_recos
