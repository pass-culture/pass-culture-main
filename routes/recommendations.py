""" user mediations routes """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from datascience import create_recommendations
from utils.config import BEFORE_AFTER_LIMIT, BLOB_SIZE
from utils.geoip import get_geolocation
from utils.human_ids import dehumanize, humanize
from utils.includes import RECOMMENDATIONS_INCLUDES
from utils.rest import expect_json_data,\
                       update

Recommendation = app.model.Recommendation
RecommendationOffer = app.model.RecommendationOffer

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
    # USER
    user_id = current_user.get_id()
    # POSITION
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    if not latitude or not longitude:
        geolocation = get_geolocation(request.remote_addr)
        if geolocation:
            latitude = geolocation.latitude
            longitude = geolocation.longitude
    print('(position) latitude', latitude, 'longitude', longitude)
    # DETERMINE AROUND
    around = request.args.get('around')
    around_recommendation = None
    if around is not None:
        around_recommendation = Recommendation.query.filter_by(
            id=dehumanize(around)
        ).first()
        print('(found) around_recommendation', around_recommendation)
    else:
        # MAYBE WE PRECISED THE MEDIATION OR OFFER ID IN THE REQUEST
        # IN ORDER TO FIND THE MATCHING USER MEDIATION
        offer_id = request.args.get('offerId')
        mediation_id = request.args.get('mediationId')
        print('(special) offer_id', offer_id, 'mediation_id', mediation_id)
        if mediation_id is not None:
            around_recommendation = Recommendation.query\
                            .filter_by(mediationId=dehumanize(mediation_id),
                                       userId=user_id).first()
            around = humanize(around_recommendation.id)
        elif offer_id is not None and offer_id != 'empty':
            around_recommendation = Recommendation.query\
                .filter(Recommendation.recommendationOffers\
                        .any(RecommendationOffer.offerId == dehumanize(offer_id)))\
                .first()
            if around_recommendation is not None:
                around = humanize(around_recommendation.id)
        if around is not None:
            print('(special) around_recommendation', around_recommendation)
    print('(query) around', around)
    # GET AROUND THE CURSOR ID PLUS SOME NOT READ YET
    query = Recommendation.query.filter_by(userId=user_id)
    unread_recommendations = query.filter_by(dateRead=None)
    # CHECK AROUND
    before_around_after_ids = []
    before_recommendations = None
    recommendations = []
    if around_recommendation is not None:
        # BEFORE AND AFTER QUERIES
        before_recommendations = query.filter(Recommendation.id < dehumanize(around))\
                          .order_by(Recommendation.id.desc())\
                          .limit(BEFORE_AFTER_LIMIT)\
                          .from_self()\
                          .order_by(Recommendation.id)
        print('(before) count', before_recommendations.count())
        after_recommendations = query.filter(Recommendation.id > dehumanize(around))\
                         .order_by(Recommendation.id)\
                         .limit(BEFORE_AFTER_LIMIT)
        print('(after) count', after_recommendations.count())
        # BEFORE AND AROUND AND AFTER IDS
        before_around_after_ids += [before_recommendation.id for before_recommendation in before_recommendations]
        print('(before) ids', list(map(humanize, before_around_after_ids)))
        if around_recommendation:
            before_around_after_ids += [around_recommendation.id]
            print('(around) id', humanize(around_recommendation.id))
        after_ids = [after_recommendation.id for after_recommendation in after_recommendations]
        print('(after) ids', list(map(humanize, after_ids)))
        before_around_after_ids += after_ids
        # CONCAT
        recommendations += list(before_recommendations)
        if around_recommendation:
            around_index = len(recommendations)
            recommendations += [around_recommendation]
        recommendations += list(after_recommendations)
    # DETERMINE IF WE NEED TO CREATE NEW RECO
    print('(before around after) count', len(before_around_after_ids))
    unread_complementary_length = BLOB_SIZE - len(before_around_after_ids)
    print('(unread) count need', unread_complementary_length)
    #unread_recommendations = unread_recommendations.filter(~Recommendation.id.in_(before_around_after_ids))\
    if before_around_after_ids:
        unread_recommendations = unread_recommendations.filter(Recommendation.id > before_around_after_ids[-1])
    unread_recommendations = unread_recommendations.order_by(Recommendation.id)
    print('(unread) count', unread_recommendations.count())
    if unread_recommendations.count() < unread_complementary_length:
        print('(check) need ' + str(unread_complementary_length) + ' unread recommendations')
        create_recommendations(
            unread_complementary_length,
            user=current_user,
            coords=latitude and longitude and { 'latitude': latitude, 'longitude': longitude }
        )
    # LIMIT UN READ
    unread_recommendations = unread_recommendations.order_by(Recommendation.dateUpdated.desc())\
                           .limit(unread_complementary_length)
    print('(unread) ids', [humanize(unread_recommendation.id) for unread_recommendation in unread_recommendations])
    recommendations += list(unread_recommendations)
    # AS DICT
    recommendations = [
        recommendation._asdict(
            include=RECOMMENDATIONS_INCLUDES,
            has_dehumanized_id=True
        )
        for recommendation in recommendations
    ]
    # ADD SOME PREVIOUS BEFORE IF recommendations has not the BLOB_SIZE
    if len(recommendations) < BLOB_SIZE:
        if len(recommendations):
            recommendations[-1]['isLast'] = True
            recommendations[-1]['blobSize'] = BLOB_SIZE
        if before_recommendations and before_recommendations.count() > 0:
            comp_size = BLOB_SIZE - len(recommendations)
            comp_before_recommendations = query.filter(Recommendation.id < before_recommendations[0].id)\
                              .order_by(Recommendation.id.desc())\
                              .limit(comp_size)\
                              .from_self()\
                              .order_by(Recommendation.id)
            recommendations = [
                recommendation._asdict(
                    has_dehumanized_id=True,
                    include=RECOMMENDATIONS_INCLUDES
                )
                for recommendation in comp_before_recommendations
            ] + recommendations
            around_index += comp_before_recommendations.count()
            print('(before comp) count', comp_before_recommendations.count())
    if around_recommendation:
        recommendations[around_index]['isAround'] = True
    # PRINT
    print('(end) ', [(recommendation['id'], recommendation['dateRead']) for recommendation in recommendations], len(recommendations))
    # RETURN
    return jsonify(recommendations),200
