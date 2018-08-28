""" bookings routes """
from datetime import datetime
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import InternalError

from domain.bookings import check_has_stock_id, check_existing_stock, check_can_book_free_offer, \
    check_offer_is_active, check_stock_booking_limit_date, check_expenses_limits, check_has_quantity
from domain.expenses import get_expenses
from models import ApiErrors, Booking, PcObject, Stock, RightsType
from utils.human_ids import dehumanize, humanize
from utils.includes import BOOKING_INCLUDES
from utils.mailing import send_booking_recap_emails, send_booking_confirmation_email_to_user
from utils.rest import expect_json_data
from utils.token import random_token


@app.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    bookings = Booking.query.filter_by(userId=current_user.id).all()
    return jsonify([booking._asdict(include=BOOKING_INCLUDES)
                    for booking in bookings]), 200


@app.route('/bookings/<booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    booking = Booking.query.filter_by(id=dehumanize(booking_id)).first_or_404()
    return jsonify(booking._asdict(include=BOOKING_INCLUDES)), 200


@app.route('/bookings', methods=['POST'])
@login_required
@expect_json_data
def create_booking():
    stock_id = request.json.get('stockId')
    recommendation_id = request.json.get('recommendationId')
    quantity = request.json.get('quantity')

    try:
        check_has_stock_id(stock_id)
        check_has_quantity(quantity)
    except ApiErrors as api_errors:
        return jsonify(api_errors.errors), 400

    stock = Stock.query.filter_by(id=dehumanize(stock_id)).first()
    managing_offerer = stock.resolvedOffer.venue.managingOfferer

    try:
        check_existing_stock(stock)
        check_can_book_free_offer(stock, current_user)
        check_offer_is_active(stock, managing_offerer)
        check_stock_booking_limit_date(stock)
    except ApiErrors as api_errors:
        return jsonify(api_errors.errors), 400

    new_booking = Booking(from_dict={
        'stockId': stock_id,
        'amount': stock.price,
        'token': random_token(),
        'userId': humanize(current_user.id),
        'quantity': quantity,
        'recommendationId': recommendation_id if recommendation_id else None
    })

    expenses = get_expenses(current_user)

    try:
        check_expenses_limits(expenses, new_booking, stock)
    except ApiErrors as api_errors:
        return jsonify(api_errors.errors), 400

    try:
        PcObject.check_and_save(new_booking)
    except InternalError as internal_error:
        api_errors = ApiErrors()
        if 'tooManyBookings' in str(internal_error.orig):
            api_errors.addError('global', 'la quantité disponible pour cette offre est atteinte')
        elif 'insufficientFunds' in str(internal_error.orig):
            api_errors.addError('insufficientFunds', 'l\'utilisateur ne dispose pas de fonds suffisants pour '
                                                     'effectuer une réservation.')
        return jsonify(api_errors.errors), 400

    new_booking_stock = Stock.query.get(new_booking.stockId)
    send_booking_recap_emails(new_booking_stock, new_booking)
    send_booking_confirmation_email_to_user(new_booking)

    return jsonify(new_booking._asdict(include=BOOKING_INCLUDES)), 201


@app.route('/bookings/<booking_id>', methods=['DELETE'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.filter_by(id=dehumanize(booking_id)).first_or_404()

    if not booking.user == current_user\
       and not current_user.hasRights(RightsType.editor,
                                      booking.stock.resolvedOffer.venue.managingOffererId):
        return "Vous n'avez pas le droit d'annuler cette réservation", 403

    booking.isCancelled = True
    PcObject.check_and_save(booking)

    return jsonify(booking._asdict(include=BOOKING_INCLUDES)), 200
