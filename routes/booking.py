""" bookings routes """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.token import create_token

Booking = app.model.Booking

@app.route('/bookings/<booking_id>', methods=['GET'])
@login_required
@expect_json_data
def get_booking(booking_id):
    user_id = current_user.get_id()
    pass
    return jsonify({}, 200

@app.route('/bookings', methods=['POST'])
@login_required
@expect_json_data
def post_booking():
    user_id = current_user.get_id()
    #Booking.filter()
    return jsonify({}, 200
