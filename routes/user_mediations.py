""" user mediations routes """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import update

from reco import make_new_recommendations
from utils.rest import expect_json_data
from utils.config import BEFORE_AFTER_LIMIT, BLOB_SIZE
from utils.human_ids import dehumanize, humanize

Offer = app.model.Offer
UserMediation = app.model.UserMediation

um_include = [
    {
        "key": "mediation",
        "sub_joins": ["event", "thing"]
    },
    {
        "key": "userMediationOffers",
        "resolve": (lambda element, filters: element['offer']),
        "sub_joins": [
            {
                "key": "offer",
                "sub_joins": ["eventOccurence", "thing", "venue"]
            }
        ]
    }
]



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
    else :
        # MAYBE WE PRECISED THE MEDIATION OR OFFER ID IN THE REQUEST
        # IN ORDER TO FIND THE MATCHING USER MEDIATION
        offer_id = request.args.get('offerId')
        mediation_id = request.args.get('mediationId')
        if mediation_id is not None:
            around_um = UserMediation.query.filter_by(mediation_id=dehumanize(mediation_id),
                userId=user_id).first()
            around = around_um.id
        elif offer_id is not None:
            around_um = UserMediation.query.filter(
                UserMediation.userMediationOffers.any(
                    Offer.id != dehumanize(offer_id)
                )
            ).first()
            around = around_um.id
            pass
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
            ums += [around_um]
        ums += list(after_ums)
    # DETERMINE IF WE NEED TO CREATE NEW RECO
    print('(before around after) count', len(before_around_after_ids))
    unread_complementary_length = BLOB_SIZE - len(before_around_after_ids)
    print('(unread) count need', unread_complementary_length)
    #unread_ums = unread_ums.filter(~UserMediation.id.in_(before_around_after_ids))\
    if len(before_around_after_ids) > 0:
        unread_ums = unread_ums.filter(UserMediation.id > before_around_after_ids[-1])
    unread_ums = unread_ums.order_by(UserMediation.id)
    print('(unread) count', unread_ums.count())
    if unread_ums.count() < unread_complementary_length:
        print('(check) create ' + str(unread_complementary_length) + ' unread ums')
        make_new_recommendations(current_user,unread_complementary_length)
    # LIMIT UN READ
    unread_ums = unread_ums.order_by(UserMediation.dateUpdated.desc())\
                           .limit(unread_complementary_length)
    print('(unread) ids', [humanize(unread_um.id) for unread_um in unread_ums])
    ums += list(unread_ums)
    # AS DICT
    ums = [um._asdict(include=um_include) for um in ums]
    print([(um['id'], um['dateRead']) for um in ums], len(ums))
    #print('dateUpdated', [um['dateUpdated'] for um in ums], len(ums))
    # ADD SOME PREVIOUS BEFORE IF NOT ALREADY
    if len(ums) < BLOB_SIZE:
        ums[-1]['isLast'] = True
        ums[-1]['blobSize'] = BLOB_SIZE
    # RETURN
    return jsonify(ums),200
