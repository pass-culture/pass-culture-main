""" bookings routes """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.rest import expect_json_data
from utils.token import random_token
from utils.human_ids import dehumanize

Booking = app.model.Booking

@app.route('/bookings/<booking_id>', methods=['GET'])
@login_required
@expect_json_data
def get_booking(booking_id):
    user_id = current_user.get_id()
    return jsonify({}, 200)

@app.route('/bookings', methods=['POST'])
@login_required
@expect_json_data
def post_booking():
    new_booking = Booking()
    new_booking.offerId = dehumanize(request.json.get('offerId'))
    token = random_token()
    print('token', token)
    new_booking.token = token
    new_booking.user = current_user
    app.model.PcObject.check_and_save(new_booking)
    return jsonify(new_booking._asdict()), 201
