""" offerers """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.internal_emails import maybe_send_offerer_validation_email
from domain.reimbursement import find_all_booking_reimbursement
from models import Offerer, PcObject, RightsType, UserOfferer
from models.venue import create_digital_venue, Venue
from repository.booking_queries import find_all_by_offerer_sorted_by_date_modified_asc
from utils.human_ids import dehumanize
from utils.includes import OFFERER_INCLUDES
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required


@app.route('/offerers', methods=['GET'])
@login_required
def list_offerers():
    query = Offerer.query
    if not current_user.isAdmin:
        query = query.join(UserOfferer) \
            .filter_by(user=current_user)
    return handle_rest_get_list(Offerer,
                                query=query,
                                include=OFFERER_INCLUDES,
                                order_by=Offerer.name)


@app.route('/offerers/<id>', methods=['GET'])
@login_required
def get_offerer(id):
    ensure_current_user_has_rights(RightsType.editor, dehumanize(id))
    offerer = load_or_404(Offerer, id)
    return jsonify(offerer._asdict(include=OFFERER_INCLUDES)), 200


@app.route('/offerers/<id>/bookings', methods=['GET'])
@login_required
def get_offerer_bookings(id):
    ensure_current_user_has_rights(RightsType.editor, dehumanize(id))
    bookings = find_all_by_offerer_sorted_by_date_modified_asc(dehumanize(id))
    bookings_reimbursements = find_all_booking_reimbursement(bookings)
    return jsonify(list(map(lambda b: b.as_dict(), bookings_reimbursements))[::-1]), 200


@app.route('/offerers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_offerer():
    offerer = Offerer()
    offerer.populateFromDict(request.json)

    digital_venue = create_digital_venue(offerer)

    PcObject.check_and_save(offerer, digital_venue)

    if not current_user.isAdmin:
        offerer.generate_validation_token()
        user_offerer = offerer.give_rights(current_user,
                                           RightsType.admin)
        PcObject.check_and_save(offerer, user_offerer)
    maybe_send_offerer_validation_email(offerer, user_offerer, app.mailjet_client.send.create)
    return jsonify(offerer._asdict(include=OFFERER_INCLUDES)), 201


@app.route('/offerers/<offererId>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_offerer(offererId):
    offerer = Offerer \
        .query.filter_by(id=dehumanize(offererId))
    offerer.populateFromDict(request.json, skipped_keys=['validationToken'])
    PcObject.check_and_save(offerer)
    return jsonify(offerer._asdict(include=OFFERER_INCLUDES)), 200
