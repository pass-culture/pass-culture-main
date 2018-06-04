""" user mediations routes """
from datetime import datetime
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from random import shuffle
from sqlalchemy import update
from sqlalchemy.sql.expression import func

from datascience import create_recommendation, create_recommendations
from models.api_errors import ApiErrors
from utils.geoip import get_geolocation
from utils.rest import expect_json_data
from utils.config import BLOB_SIZE, BLOB_READ_NUMBER,\
                         BLOB_UNREAD_NUMBER
from utils.human_ids import dehumanize, humanize
from utils.includes import RECOMMENDATIONS_INCLUDES,\
                           RECOMMENDATION_OFFER_INCLUDES
from utils.rest import expect_json_data,\
                       update

Event = app.model.Event
Mediation = app.model.Mediation
Offer = app.model.Offer
Recommendation = app.model.Recommendation
Thing = app.model.Thing


def find_or_make_recommendation(user, occasion_type, occasion_id,
                                mediation_id, from_user_id=None):
    query = Recommendation.query
    print('(special) offer_id', occasion_id, 'mediation_id', mediation_id)
    if not mediation_id and not (occasion_id and occasion_type):
        return None
    if mediation_id:
        filter = (Recommendation.mediationId == mediation_id)
    elif occasion_id and occasion_type:
        if occasion_type == 'thing':
            filter = (Recommendation.thingId == mediation_id)
        elif occasion_type == 'event':
            filter = (Recommendation.eventId == mediation_id)
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
            occasion = Thing.query.get(occasion_id)
        elif occasion_type == 'event':
            occasion = Event.query.get(occasion_id)
        mediation = Mediation.query.get(mediation_id)
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
    requested_recommendation = find_or_make_recommendation(current_user,
                                                           request.args.get('occasionType'),
                                                           dehumanize(request.args.get('occasionId')),
                                                           dehumanize(request.args.get('mediationId')))
    print('(special) requested_recommendation', requested_recommendation)

    # we get more read+unread recos than needed in case we can't make enough new recos
    query = Recommendation.query.outerjoin(Mediation)\
                                .filter((Recommendation.user == current_user)
                                        & (Mediation.tutoIndex == None)
                                        & ((Recommendation.validUntilDate == None)
                                           | (Recommendation.validUntilDate > datetime.now())))

    unread_recos = query.filter(Recommendation.dateRead == None)\
                                  .order_by(func.random())\
                                  .limit(BLOB_SIZE)\
                                  .all()
    #print('(unread recos)', unread_recos)
    print('(unread reco) count', len(unread_recos))

    read_recos = query.filter(Recommendation.dateRead != None)\
                      .order_by(func.random())\
                      .limit(BLOB_SIZE)\
                      .all()
    #print('(read recos)', read_recos)
    print('(read reco) count', len(read_recos))

    needed_new_recos = BLOB_SIZE\
                       - min(len(unread_recos), BLOB_UNREAD_NUMBER)\
                       - min(len(read_recos), BLOB_READ_NUMBER)

    print('(needed new recos) count', needed_new_recos)

    new_recos = create_recommendations(needed_new_recos,
                                       user=current_user)

    print('(new recos)', [(reco, reco.mediation, reco.dateRead) for reco in new_recos])
    print('(new reco) count', len(new_recos))

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
                                                       & (Recommendation.dateRead != None))\
                                               .count()

    print('(all read recos) count', all_read_recos_count)

    tuto_recos = Recommendation.query.join(Mediation)\
                               .filter((Mediation.tutoIndex != None)
                                       & (Recommendation.user == current_user))\
                               .order_by(Mediation.tutoIndex)\
                               .all()
    print('(tuto recos) count', len(tuto_recos))

    tutos_read = 0
    for tuto_reco in tuto_recos:
        if tuto_reco.dateRead is not None:
            tutos_read += 1
        elif len(recos) >= tuto_reco.mediation.tutoIndex-tutos_read:
            recos = recos[:tuto_reco.mediation.tutoIndex-tutos_read]\
                    + [tuto_reco]\
                    + recos[tuto_reco.mediation.tutoIndex-tutos_read:]

    if requested_recommendation:
        for i, reco in enumerate(recos):
            if reco.id == requested_recommendation.id:
                recos = recos[:i]+recos[i+1:]
                break
        recos = [requested_recommendation] + recos

    print('(recap reco) ',
          [(reco, reco.mediation, reco.dateRead) for reco in recos],
          len(recos))

    # FIXME: This is to support legacy code in the webapp
    # it should be removed once all requests from the webapp
    # have an app version header, which will mean that all
    # clients (or at least those who do use the app) have
    # a recent version of the app

    dict_recos = list(map(lambda r: r._asdict(include=RECOMMENDATIONS_INCLUDES),
                          recos))

    for index, reco in enumerate(dict_recos):
        rbs = []
        for b in recos[index].bookings:
            rb = {}
            rb['booking'] = b
            rbs.append(rb)
        reco['recommendationBookings'] = rbs

        if recos[index].event:
            ros = map(lambda eo: eo.offers[0]._asdict(include=RECOMMENDATION_OFFER_INCLUDES),
                      recos[index].event.occurences)
            reco['recommendationOffers'] = ros

    # RETURN
    return jsonify(dict_recos), 200
