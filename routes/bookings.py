""" bookings routes """
from datetime import datetime

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import InternalError

from models import Booking
from models.api_errors import ApiErrors
from models.pc_object import PcObject
from models.stock import Stock
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


def _check_has_stock_id(stock_id):
    if stock_id is None:
        api_errors = ApiErrors()
        api_errors.addError('stockId', 'Vous devez préciser un identifiant d\'offre')
        raise api_errors


def _check_existing_stock(stock):
    if stock is None:
        api_errors = ApiErrors()
        api_errors.addError('stockId', 'stockId ne correspond à aucun stock')
        raise api_errors


def _check_can_book_free_offer(stock, user):
    if (user.canBookFreeOffers == False) and (stock.price == 0):
        api_errors = ApiErrors()
        api_errors.addError('cannotBookFreeOffers', 'L\'utilisateur n\'a pas le droit de réserver d\'offres gratuites')
        raise api_errors


def _check_offer_is_active(stock, offerer):
    if not stock.isActive or not offerer.isActive or (stock.eventOccurrence and (not stock.eventOccurrence.isActive)):
        api_errors = ApiErrors()
        api_errors.addError('stockId', "Cette offre a été retirée. Elle n'est plus valable.")
        raise api_errors


def _check_stock_booking_limit_date(stock):
    if stock.bookingLimitDatetime is not None and stock.bookingLimitDatetime < datetime.utcnow():
        api_errors = ApiErrors()
        api_errors.addError('global', 'La date limite de réservation de cette offre est dépassée')
        raise api_errors


@app.route('/bookings', methods=['POST'])
@login_required
@expect_json_data
def create_booking():
    stock_id = request.json.get('stockId')
    recommendation_id = request.json.get('recommendationId')

    try:
        _check_has_stock_id(stock_id)
    except ApiErrors as api_errors:
        return jsonify(api_errors.errors), 400

    stock = Stock.query.filter_by(id=dehumanize(stock_id)).first()
    managing_offerer = stock.resolvedOffer.venue.managingOfferer

    try:
        _check_existing_stock(stock)
        _check_can_book_free_offer(stock, current_user)
        _check_offer_is_active(stock, managing_offerer)
        _check_stock_booking_limit_date(stock)
    except ApiErrors as api_errors:
        return jsonify(api_errors.errors), 400

    new_booking = Booking(from_dict={
        'stockId': stock_id,
        'amount': stock.price,
        'token': random_token(),
        'userId': humanize(current_user.id),
        'recommendationId': recommendation_id if recommendation_id else None
    })

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
