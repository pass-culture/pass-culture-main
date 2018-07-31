""" bookings routes """
from datetime import datetime

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import InternalError

from models import Booking, Venue
from models.api_errors import ApiErrors
from models.stock import Stock
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.includes import BOOKING_INCLUDES
from utils.mailing import send_booking_recap_emails, send_booking_confirmation_email_to_user
from utils.rest import expect_json_data
from utils.token import random_token
from utils.logger import logger


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
def post_booking():
    stock_id = request.json.get('stockId')
    ae = ApiErrors()

    if current_user.canBook == False:
        ae.addError('canBook', 'L\'utilisateur n\'a pas le droit de réserver d\'offre')
        return jsonify(ae.errors), 400

    if stock_id is None:
        ae.addError('stockId', 'Vous devez préciser un identifiant d\'offre')
        return jsonify(ae.errors), 400

    stock = Stock.query.filter_by(id=dehumanize(stock_id)).first()

    if stock is None:
        ae.addError('stockId', 'stockId ne correspond à aucune stock')
        return jsonify(ae.errors), 400

    if (current_user.canBookFreeOffers == False) and (offer.price == 0):
        ae.addError('cannotBookFreeOffers', 'L\'utilisateur n\'a pas le droit de réserver d\'offres gratuites')
        return jsonify(ae.errors), 400

    managingOfferer = stock.resolvedOccasion.venue.managingOfferer
    if not stock.isActive or\
       not managingOfferer.isActive or\
       (stock.eventOccurrence and (not stock.eventOccurrence.isActive)):
        ae.addError('stockId', "Cette offre a été retirée. Elle n'est plus valable.")
        return jsonify(ae.errors), 400

    if stock.bookingLimitDatetime is not None and\
       stock.bookingLimitDatetime < datetime.utcnow():
        ae.addError('global', 'La date limite de réservation de cette offre'
                              + ' est dépassée')
        return jsonify(ae.errors), 400

    new_booking = Booking()
    new_booking.stockId = dehumanize(stock_id)

    amount = stock.price
    new_booking.amount = amount

    token = random_token()
    new_booking.token = token
    new_booking.user = current_user
    recommendation_id = request.json.get('recommendationId')
    if recommendation_id is not None:
        new_booking.recommendationId = dehumanize(recommendation_id)

    try:
        PcObject.check_and_save(new_booking)
    except InternalError as ie:
        if 'check_booking' in str(ie.orig):
            if 'tooManyBookings' in str(ie.orig):
                ae.addError('global', 'la quantité disponible pour cette offre'
                            + ' est atteinte')
            elif 'insufficientFunds' in str(ie.orig):
                ae.addError('insufficientFunds', 'l\'utilisateur ne dispose pas'
                            + ' de fonds suffisants pour effectuer'
                            + ' une réservation.')
            return jsonify(ae.errors), 400
        else:
            raise ie

    new_booking_stock = Stock.query.get(new_booking.stockId)
    send_booking_recap_emails(new_booking_stock, new_booking)
    send_booking_confirmation_email_to_user(new_booking)

    return jsonify(new_booking._asdict(include=BOOKING_INCLUDES)), 201
