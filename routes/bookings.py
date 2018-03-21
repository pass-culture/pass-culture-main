""" bookings routes """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from models.api_errors import ApiErrors
from utils.rest import expect_json_data
from utils.token import random_token
from utils.human_ids import dehumanize

Booking = app.model.Booking

@app.route('/bookings/<booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    print('booking_id', booking_id)
    booking = Booking.query.filter_by(id=dehumanize(booking_id)).first_or_404()
    return jsonify(booking._asdict()), 200

@app.route('/bookings', methods=['POST'])
@login_required
@expect_json_data
def post_booking():
    offer_id = request.json.get('offerId')
    if offer_id is None:
        e = ApiErrors()
        e.addError('offerId', 'Vous devez adjoindre une offer')
        return jsonify(e.errors), 400
    new_booking = Booking()
    new_booking.offerId = dehumanize(offer_id)
    token = random_token()
    new_booking.token = token
    new_booking.user = current_user
    user_mediation_id = request.json.get('userMediationId')
    if user_mediation_id is not None:
        new_booking.userMediationId = dehumanize(user_mediation_id)
    app.model.PcObject.check_and_save(new_booking)
    return jsonify(new_booking._asdict()), 201
