from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func, update

from reco import make_new_recommendations
from utils.rest import expect_json_data
from utils.config import BLOB_LIMIT, RECO_LIMIT
from utils.human_ids import dehumanize, humanize

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
                "sub_joins": ["eventOccurence","thing"]
            }
        ]
    }
]



@app.route('/userMediations', methods=['PUT'])
@login_required
@expect_json_data
def update_user_mediations():
    print('current_user', current_user)
    user_id = current_user.get_id()
    # DETERMINE AROUND
    around = request.args.get('around')
    print('(query) around', around)
    if around is None:
        max_date_updated = app.db.session\
                                 .query(func.max(UserMediation.dateUpdated))\
                                 .filter(UserMediation.userId == user_id)\
                                 .first()
        around_um = UserMediation.query\
                                 .filter(
                                     UserMediation.userId == user_id,
                                     UserMediation.dateUpdated == max_date_updated
                                 )\
                                 .first()
        if around_um is not None:
            around = humanize(around_um.id)
    else:
        around_um = UserMediation.query.filter_by(id=dehumanize(around)).first()
    # UPDATE FROM CLIENT LOCAL BUFFER
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
    # CHECK IF WE NEED TO MAKE NEW RECO
    unread_count = UserMediation.query\
                                .filter_by(userId=user_id, dateRead=None)\
                                .count()
    print('(update) unread count', unread_count)
    if unread_count < BLOB_LIMIT:
        print('Create new')
        make_new_recommendations(current_user, RECO_LIMIT)
    # GET AROUND THE CURSOR ID PLUS SOME NOT READ YET
    query = UserMediation.query.filter_by(userId=user_id)\
                               .order_by(UserMediation.id)
    unread_ums = query.filter_by(dateRead=None)
    print('(reco) unread count', unread_ums.count())
    # INIT
    ums = []
    # CHECK AROUND
    print('around', around)
    if around is not None:
        before_ums = query.filter(UserMediation.id < dehumanize(around))\
                          .limit(BLOB_LIMIT)
        print('before count', before_ums.count())
        after_ums = query.filter(UserMediation.id > dehumanize(around))\
                         .limit(BLOB_LIMIT)
        print('after count', after_ums.count())
        unread_ums = unread_ums.filter(~UserMediation.id.in_(
            [before_um.id for before_um in before_ums] + [around_um.id]))\
                      .filter(~UserMediation.id.in_(
                          [after_um.id for after_um in after_ums]))
        ums = list(before_ums) + [around_um] + list(after_ums)
    # LIMIT UN READ
    unread_ums = unread_ums.order_by(UserMediation.dateUpdated.desc())\
                           .limit(RECO_LIMIT)
    print('(limit) unread count', unread_ums.count())
    ums += list(unread_ums)
    # CONCAT
    ums = [um._asdict(include=um_include) for um in ums]
    print([um['dateRead'] for um in ums], len(ums))
    print([um['dateUpdated'] for um in ums], len(ums))
    # RETURN
    return jsonify(ums),200
