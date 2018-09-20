""" bookings routes """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.expenses import get_expenses
from domain.user_emails import send_user_driven_cancellation_email_to_user, \
    send_user_driven_cancellation_email_to_offerer, send_offerer_driven_cancellation_email_to_user, \
    send_offerer_driven_cancellation_email_to_offerer, send_booking_recap_emails, \
    send_booking_confirmation_email_to_user
from models import ApiErrors, Booking, PcObject, Stock, RightsType
from models.pc_object import serialize
from repository import booking_queries
from utils.human_ids import dehumanize, humanize
from utils.includes import BOOKING_INCLUDES
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data
from utils.token import random_token
from validation.bookings import check_booking_not_already_used, \
    check_booking_not_cancelled, \
    check_can_book_free_offer, \
    check_existing_stock, \
    check_expenses_limits, \
    check_has_quantity, \
    check_has_stock_id, \
    check_offer_is_active, \
    check_stock_booking_limit_date, \
    check_user_is_logged_in_or_email_is_provided, check_email_and_offer_id_for_anonymous_user


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

    stock = Stock.queryNotSoftDeleted().filter_by(id=dehumanize(stock_id)).first()
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

    check_expenses_limits(expenses, new_booking, stock)
    booking_queries.save_booking(new_booking)

    new_booking_stock = Stock.query.get(new_booking.stockId)
    send_booking_recap_emails(new_booking, app.mailjet_client.send.create)
    send_booking_confirmation_email_to_user(new_booking, app.mailjet_client.send.create)

    return jsonify(new_booking._asdict(include=BOOKING_INCLUDES)), 201


@app.route('/bookings/<booking_id>', methods=['DELETE'])
@login_required
def cancel_booking(booking_id):
    booking = booking_queries.find_by_id(dehumanize(booking_id))

    is_user_cancellation = booking.user == current_user
    booking_offerer = booking.stock.resolvedOffer.venue.managingOffererId
    is_offerer_cancellation = current_user.hasRights(RightsType.editor, booking_offerer)

    if not is_user_cancellation and not is_offerer_cancellation:
        return "Vous n'avez pas le droit d'annuler cette réservation", 403

    booking.isCancelled = True
    PcObject.check_and_save(booking)

    if is_user_cancellation:
        send_user_driven_cancellation_email_to_user(booking, app.mailjet_client.send.create)
        send_user_driven_cancellation_email_to_offerer(booking, app.mailjet_client.send.create)

    if is_offerer_cancellation:
        send_offerer_driven_cancellation_email_to_user(booking, app.mailjet_client.send.create)
        send_offerer_driven_cancellation_email_to_offerer(booking, app.mailjet_client.send.create)

    return jsonify(booking._asdict(include=BOOKING_INCLUDES)), 200


@app.route('/bookings/token/<token>', methods=["GET"])
def get_booking_by_token(token):
    email = request.args.get('email', None)
    offer_id = dehumanize(request.args.get('offer_id', None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking = booking_queries.find_by(token, email, offer_id)

    offer_name = booking.stock.resolvedOffer.eventOrThing.name
    date = None
    if booking.stock.eventOccurrence:
        date = serialize(booking.stock.eventOccurrence.beginningDatetime)
    offerer_id = booking.stock.resolvedOffer.venue.managingOffererId
    venue_departement_code = booking.stock.resolvedOffer.venue.departementCode

    current_user_can_validate_bookings = current_user.is_authenticated and current_user.hasRights(RightsType.editor,
                                                                                                  offerer_id)
    if current_user_can_validate_bookings:
        response = {'bookingId': humanize(booking.id), 'email': booking.user.email, 'userName': booking.user.publicName,
                    'offerName': offer_name, 'date': date, 'isUsed': booking.isUsed,
                    'venueDepartementCode': venue_departement_code}
        return jsonify(response), 200
    return '', 204


@app.route('/bookings/token/<token>', methods=["PATCH"])
def patch_booking_by_token(token):
    email = request.args.get('email', None)
    offer_id = dehumanize(request.args.get('offer_id', None))
    booking = booking_queries.find_by(token, email, offer_id)

    if current_user.is_authenticated:
        ensure_current_user_has_rights(RightsType.editor, booking.stock.resolvedOffer.venue.managingOffererId)
    else:
        check_email_and_offer_id_for_anonymous_user(email, offer_id)

    check_booking_not_cancelled(booking)
    check_booking_not_already_used(booking)
    booking.isUsed = True
    PcObject.check_and_save(booking)
    return '', 204
