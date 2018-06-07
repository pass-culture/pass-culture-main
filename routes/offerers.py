""" offerers """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.human_ids import dehumanize
from utils.includes import OFFERERS_INCLUDES
from utils.rest import expect_json_data,\
                       update,\
                       handle_rest_get_list,\
                       login_or_api_key_required

def check_offerer_user(query):
    return query.filter(
        app.model.Offerer.users.any(app.model.User.id == current_user.id)
    )\
    .first_or_404()


@app.route('/offerers', methods=['GET'])
@login_required
def list_offerers():
    return handle_rest_get_list(app.model.Offerer,
                                include=OFFERERS_INCLUDES)


@app.route('/offerers/<offererId>', methods=['GET'])
@login_required
def get_offerer(offererId):
    query = app.model.Offerer.query.filter_by(id=dehumanize(offererId))\
                         .first_or_404()\
                         .query
    check_offerer_user(query)
    return jsonify(query._asdict(include=OFFERERS_INCLUDES))


@app.route('/offerers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_offerer():
    offerer = app.model.Offerer()
    update(offerer, request.json)
    if current_user:
        user_offerer = app.model.UserOfferer()
        user_offerer.offerer = offerer
        user_offerer.user = current_user
        user_offerer.rights = app.model.RightsType.admin
        app.db.session.add(user_offerer)



    app.model.PcObject.check_and_save(offerer)
    return jsonify(offerer._asdict(include=OFFERERS_INCLUDES)), 201

@app.route('/offerers/<offererId>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_offerer(offererId):
    offerer = app.model.Offerer\
                       .query.filter_by(id=dehumanize(offererId))
    update(offerer, request.json)
    app.model.PcObject.check_and_save(offerer)
    return jsonify(offerer._asdict(include=OFFERERS_INCLUDES)), 200
