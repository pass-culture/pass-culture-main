""" offerers """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.human_ids import dehumanize
from utils.includes import OFFERER_INCLUDES
from utils.mailing import maybe_send_offerer_validation_email
from utils.rest import ensure_current_user_has_rights,\
                       expect_json_data,\
                       handle_rest_get_list,\
                       load_or_404,\
                       login_or_api_key_required,\
                       update

Offerer = app.model.Offerer
RightsType = app.model.RightsType
UserOfferer = app.model.UserOfferer


def check_offerer_user(query):
    return query.filter(
        app.model.Offerer.users.any(app.model.User.id == current_user.id)
    ).first_or_404()


@app.route('/offerers', methods=['GET'])
@login_required
def list_offerers():
    query = app.model.Offerer.query
    if not current_user.isAdmin:
        query = query.join(UserOfferer)\
                     .filter_by(user=current_user)
    return handle_rest_get_list(Offerer,
                                query=query,
                                include=OFFERER_INCLUDES)

@app.route('/offerers/<id>', methods=['GET'])
@login_required
def get_offerer(id):
    ensure_current_user_has_rights(RightsType.editor, id)
    offerer = load_or_404(Offerer, id)
    return jsonify(offerer._asdict(include=OFFERER_INCLUDES)), 200


@app.route('/offerers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_offerer():
    offerer = app.model.Offerer()
    update(offerer, request.json)
    if not current_user.isAdmin:
        offerer.generate_validation_token()
        user_offerer = offerer.give_rights(current_user,
                                           app.model.RightsType.admin)
    app.model.PcObject.check_and_save(offerer, user_offerer)
    maybe_send_offerer_validation_email(current_user, offerer)
    return jsonify(offerer._asdict(include=OFFERER_INCLUDES)), 201


@app.route('/offerers/<offererId>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_offerer(offererId):
    offerer = app.model.Offerer\
                       .query.filter_by(id=dehumanize(offererId))
    update(offerer, request.json)
    app.model.PcObject.check_and_save(offerer)
    return jsonify(offerer._asdict(include=OFFERER_INCLUDES)), 200
