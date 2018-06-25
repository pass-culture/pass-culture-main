""" offerers """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from models.api_errors import ApiErrors
from utils.human_ids import dehumanize
from utils.includes import OFFERERS_INCLUDES, VENUES_INCLUDES
from utils.mailing import send_pro_validation_email
from utils.rest import expect_json_data,\
                       handle_rest_get_list,\
                       login_or_api_key_required,\
                       update

Offerer = app.model.Offerer
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
                                include=OFFERERS_INCLUDES)


@app.route('/offerers/<id>/venues', methods=['GET'])
@login_required
def list_offerers_venues(id):
    dehumanize_id = dehumanize(id)
    for offerer in current_user.offerers:
        if offerer.id == dehumanize_id:
            venues = [
                o._asdict(include=VENUES_INCLUDES)
                for o in offerer.managedVenues
            ]
            return jsonify(venues), 200
    e = ApiErrors()
    e.addError('global', "Cette structure n'est pas enregistrée chez cet utilisateur.")
    return jsonify(e.errors), 400


@app.route('/offerers/<id>', methods=['GET'])
@login_required
def get_offerer(id):
    dehumanize_id = dehumanize(id)
    for offerer in current_user.offerers:
        if offerer.id == dehumanize_id:
            return jsonify(offerer._asdict(include=OFFERERS_INCLUDES)), 200
    e = ApiErrors()
    e.addError('global', "Cette structure n'est pas enregistrée chez cet utilisateur.")
    return jsonify(e.errors), 400


@app.route('/offerers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_offerer():
    offerer = app.model.Offerer()
    update(offerer, request.json)
    offerer.make_admin(current_user)
    offerer.isActive = False
    app.model.PcObject.check_and_save(offerer)
    send_pro_validation_email(current_user, offerer)
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
