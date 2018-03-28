""" user mediations routes """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import update

from recommendations import get_recommendations
from utils.rest import expect_json_data
from utils.config import BEFORE_AFTER_LIMIT, BLOB_SIZE
from utils.human_ids import dehumanize, humanize
from utils.includes import user_mediations_includes

Offer = app.model.Offer
UserMediation = app.model.UserMediation
UserMediationOffer = app.model.UserMediationOffer

@app.route('/userMediations', methods=['PUT'])
@login_required
@expect_json_data
def update_user_mediations():
    # USER
    user_id = current_user.get_id()
    # DETERMINE AROUND
    around = request.args.get('around')
    around_um = None
    print('(query) around', around)
    if around is not None:
        around_um = UserMediation.query.filter_by(id=dehumanize(around)).first()
        print('(found) around_um', around_um)
    else:
        # MAYBE WE PRECISED THE MEDIATION OR OFFER ID IN THE REQUEST
        # IN ORDER TO FIND THE MATCHING USER MEDIATION
        offer_id = request.args.get('offerId')
        mediation_id = request.args.get('mediationId')
        print('(special) offer_id', offer_id, 'mediation_id', mediation_id)
        if mediation_id is not None:
            around_um = UserMediation.query\
                            .filter_by(mediation_id=dehumanize(mediation_id),
                                       userId=user_id).first()
            around = humanize(around_um.id)
        elif offer_id is not None:
            around_um = UserMediation.query\
                .filter(UserMediation.userMediationOffers\
                        .any(UserMediationOffer.offerId == dehumanize(offer_id)))\
                .first()
            around = humanize(around_um.id)
        if around is not None:
            print('(special) around_um', around_um)
    # UPDATE FROM CLIENT LOCAL BUFFER
    print('(update) maybe')
    for um in request.json:
        print("um['id'], um['dateRead']", um['id'], um['dateRead'])
        update_query = update(UserMediation)\
                   .where((UserMediation.userId == user_id) &
                          (UserMediation.id == dehumanize(um['id'])))\
                   .values({
                       'dateRead': um['dateRead'],
                       'dateUpdated': um['dateUpdated'],
                       'isFavorite': um['isFavorite']})
        app.db.session.execute(update_query)
    app.db.session.commit()
    # GET AROUND THE CURSOR ID PLUS SOME NOT READ YET
    query = UserMediation.query.filter_by(userId=user_id)
    unread_ums = query.filter_by(dateRead=None)
    # CHECK AROUND
    before_around_after_ids = []
    before_ums = None
    ums = []
    if around_um is not None:
        # BEFORE AND AFTER QUERIES
        before_ums = query.filter(UserMediation.id < dehumanize(around))\
                          .order_by(UserMediation.id.desc())\
                          .limit(BEFORE_AFTER_LIMIT)\
                          .from_self()\
                          .order_by(UserMediation.id)
        print('(before) count', before_ums.count())
        after_ums = query.filter(UserMediation.id > dehumanize(around))\
                         .order_by(UserMediation.id)\
                         .limit(BEFORE_AFTER_LIMIT)
        print('(after) count', after_ums.count())
        # BEFORE AND AROUND AND AFTER IDS
        before_around_after_ids += [before_um.id for before_um in before_ums]
        print('(before) ids', list(map(humanize, before_around_after_ids)))
        if around_um:
            before_around_after_ids += [around_um.id]
            print('(around) id', humanize(around_um.id))
        after_ids = [after_um.id for after_um in after_ums]
        print('(after) ids', list(map(humanize, after_ids)))
        before_around_after_ids += after_ids
        # CONCAT
        ums += list(before_ums)
        if around_um:
            around_index = len(ums)
            ums += [around_um]
        ums += list(after_ums)
    # DETERMINE IF WE NEED TO CREATE NEW RECO
    print('(before around after) count', len(before_around_after_ids))
    unread_complementary_length = BLOB_SIZE - len(before_around_after_ids)
    print('(unread) count need', unread_complementary_length)
    #unread_ums = unread_ums.filter(~UserMediation.id.in_(before_around_after_ids))\
    if before_around_after_ids:
        unread_ums = unread_ums.filter(UserMediation.id > before_around_after_ids[-1])
    unread_ums = unread_ums.order_by(UserMediation.id)
    print('(unread) count', unread_ums.count())
    if unread_ums.count() < unread_complementary_length:
        print('(check) need ' + str(unread_complementary_length) + ' unread ums')
        get_recommendations(current_user, unread_complementary_length)
    # LIMIT UN READ
    unread_ums = unread_ums.order_by(UserMediation.dateUpdated.desc())\
                           .limit(unread_complementary_length)
    print('(unread) ids', [humanize(unread_um.id) for unread_um in unread_ums])
    ums += list(unread_ums)
    # AS DICT
    ums = [um._asdict(include=user_mediations_includes) for um in ums]
    # ADD SOME PREVIOUS BEFORE IF ums has not the BLOB_SIZE
    if len(ums) < BLOB_SIZE:
        ums[-1]['isLast'] = True
        ums[-1]['blobSize'] = BLOB_SIZE
        if before_ums and before_ums.count() > 0:
            comp_size = BLOB_SIZE - len(ums)
            comp_before_ums = query.filter(UserMediation.id < before_ums[0].id)\
                              .order_by(UserMediation.id.desc())\
                              .limit(comp_size)\
                              .from_self()\
                              .order_by(UserMediation.id)
            ums = [um._asdict(include=user_mediations_includes) for um in comp_before_ums] + ums
            around_index += comp_before_ums.count()
    if around_um:
        ums[around_index]['isAround'] = True
    # PRINT
    print('(end) ', [(um['id'], um['dateRead']) for um in ums], len(ums))
    # RETURN
    return jsonify(ums),200
