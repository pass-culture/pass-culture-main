""" bookings routes """

from itertools import chain

import dateutil
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.bookings import generate_bookings_details_csv
from domain.expenses import get_expenses
from domain.user_activation import create_initial_deposit, check_is_activation_booking
from domain.user_emails import send_booking_recap_emails, \
    send_booking_confirmation_email_to_user, send_cancellation_emails_to_user_and_offerer, \
    send_activation_notification_email
from models import ApiErrors, Booking, PcObject, Stock, RightsType, EventType, Offerer
from models.offer_type import ProductType
from models.pc_object import serialize
from repository import booking_queries
from repository.booking_queries import find_active_bookings_by_user_id, \
    find_all_bookings_for_stock_and_user, \
    find_all_offerer_bookings, find_all_digital_bookings_for_offerer
from repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from utils.human_ids import dehumanize, humanize
from utils.includes import BOOKING_INCLUDES
from utils.mailing import MailServiceException, send_raw_email
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data
from utils.token import random_token
from validation.bookings import check_booking_is_usable, \
    check_can_book_free_offer, \
    check_existing_stock, \
    check_expenses_limits, \
    check_has_quantity, \
    check_has_stock_id, \
    check_already_booked, \
    check_booking_quantity_limit, \
    check_not_soft_deleted_stock, \
    check_offer_date, \
    check_offer_is_active, \
    check_stock_booking_limit_date, \
    check_user_is_logged_in_or_email_is_provided, check_email_and_offer_id_for_anonymous_user, \
    check_booking_is_cancellable, check_stock_venue_is_validated, check_rights_for_activation_offer, \
    check_rights_to_get_bookings_csv
from validation.users import check_user_can_validate_bookings


@app.route('/bookings/csv', methods=['GET'])
@login_required
def get_bookings_csv():
    only_digital_venues = request.args.get('onlyDigitalVenues', False)

    try:
        venue_id = dehumanize(request.args.get('venueId', None))
        offer_id = dehumanize(request.args.get('offerId', None))
    except ValueError:
        errors = ApiErrors()
        errors.add_error(
            'global',
            'Les identifiants sont incorrects'
        )
        errors.status_code = 400
        raise errors

    try:
        if request.args.get('dateFrom', None):
            date_from = dateutil.parser.parse(request.args.get('dateFrom'))
        else:
            date_from = None
        if request.args.get('dateTo', None):
            date_to = dateutil.parser.parse(request.args.get('dateTo'))
        else:
            date_to = None
    except ValueError:
        errors = ApiErrors()
        errors.add_error(
            'global',
            'Les dates sont incorrectes'
        )
        errors.status_code = 400
        raise errors
    check_rights_to_get_bookings_csv(current_user, venue_id, offer_id)

    query = filter_query_where_user_is_user_offerer_and_is_validated(Offerer.query,
                                                                     current_user)
    if only_digital_venues:
        bookings = chain(*list(map(lambda offerer: find_all_digital_bookings_for_offerer(offerer.id, offer_id, date_from, date_to),
                                   query)))
    else:
        bookings = chain(*list(map(lambda offerer: find_all_offerer_bookings(offerer.id, venue_id, offer_id, date_from, date_to),
                                   query)))

    bookings_csv = generate_bookings_details_csv(bookings)

    return bookings_csv.encode('utf-8-sig'), \
           200, \
           {'Content-type': 'text/csv; charset=utf-8;',
            'Content-Disposition': 'attachment; filename=reservations_pass_culture.csv'}


@app.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    bookings = Booking.query.filter_by(userId=current_user.id).all()
    return jsonify([booking.as_dict(include=BOOKING_INCLUDES)
                    for booking in bookings]), 200


@app.route('/bookings/<booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    booking = Booking.query.filter_by(id=dehumanize(booking_id)).first_or_404()
    return jsonify(booking.as_dict(include=BOOKING_INCLUDES)), 200


@app.route('/bookings', methods=['POST'])
@login_required
@expect_json_data
def create_booking():
    stock_id = request.json.get('stockId')
    recommendation_id = request.json.get('recommendationId')
    quantity = request.json.get('quantity')

    stock = Stock.query.filter_by(id=dehumanize(stock_id)).first()

    try:
        check_has_stock_id(stock_id)
        check_existing_stock(stock)
        user_bookings = find_all_bookings_for_stock_and_user(stock, current_user)
        check_already_booked(user_bookings)
        check_has_quantity(quantity)
        check_booking_quantity_limit(quantity)
        check_offer_date(stock)
        check_not_soft_deleted_stock(stock)
        check_can_book_free_offer(stock, current_user)
        check_offer_is_active(stock)
        check_stock_booking_limit_date(stock)
        check_stock_venue_is_validated(stock)
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

    bookings = find_active_bookings_by_user_id(current_user.id)

    expenses = get_expenses(bookings)
    check_expenses_limits(expenses, new_booking)
    PcObject.save(new_booking)

    try:
        send_booking_recap_emails(new_booking, send_raw_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)
    try:
        send_booking_confirmation_email_to_user(new_booking, send_raw_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return jsonify(new_booking.as_dict(include=BOOKING_INCLUDES)), 201


@app.route('/bookings/<booking_id>', methods=['PATCH'])
@login_required
def patch_booking(booking_id):
    is_cancelled = request.json.get('isCancelled')

    if is_cancelled is not True:
        api_errors = ApiErrors()
        api_errors.add_error(
            'isCancelled',
            "Vous pouvez seulement changer l'état isCancelled à vrai"
        )
        raise api_errors

    booking = booking_queries.find_by_id(dehumanize(booking_id))

    is_user_cancellation = booking.user == current_user
    check_booking_is_cancellable(booking, is_user_cancellation)
    booking_offerer = booking.stock.resolvedOffer.venue.managingOffererId
    is_offerer_cancellation = current_user.hasRights(RightsType.editor, booking_offerer)

    if not is_user_cancellation and not is_offerer_cancellation:
        return "Vous n'avez pas le droit d'annuler cette réservation", 403

    booking.isCancelled = True
    PcObject.save(booking)

    try:
        send_cancellation_emails_to_user_and_offerer(booking, is_offerer_cancellation, is_user_cancellation,
                                                     send_raw_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return jsonify(booking.as_dict(include=BOOKING_INCLUDES)), 200


@app.route('/bookings/token/<token>', methods=["GET"])
def get_booking_by_token(token):
    email = request.args.get('email', None)
    offer_id = dehumanize(request.args.get('offer_id', None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking_token_upper_case = token.upper()
    booking = booking_queries.find_by(booking_token_upper_case, email, offer_id)
    check_booking_is_usable(booking)

    offerer_id = booking.stock.resolvedOffer.venue.managingOffererId

    current_user_can_validate_booking = check_user_can_validate_bookings(current_user, offerer_id)
    if current_user_can_validate_booking:
        response = _create_response_to_get_booking_by_token(booking)
        return jsonify(response), 200
    return '', 204


@app.route('/bookings/token/<token>', methods=["PATCH"])
def patch_booking_by_token(token):
    email = request.args.get('email', None)
    offer_id = dehumanize(request.args.get('offer_id', None))
    booking_token_upper_case = token.upper()
    booking = booking_queries.find_by(booking_token_upper_case, email, offer_id)

    if current_user.is_authenticated:
        ensure_current_user_has_rights(RightsType.editor, booking.stock.resolvedOffer.venue.managingOffererId)
    else:
        check_email_and_offer_id_for_anonymous_user(email, offer_id)

    check_booking_is_usable(booking)
    booking.isUsed = True

    if check_is_activation_booking(booking):
        activate_user(booking.user)
        send_activation_notification_email(booking.user, send_raw_email)

    PcObject.save(booking)
    return '', 204


def activate_user(user_to_activate):
    check_rights_for_activation_offer(current_user)
    user_to_activate.canBookFreeOffers = True
    deposit = create_initial_deposit(user_to_activate)
    PcObject.save(deposit)


def _create_response_to_get_booking_by_token(booking):
    offer_name = booking.stock.resolvedOffer.product.name
    date = None
    product = booking.stock.resolvedOffer.product
    is_event = ProductType.is_event(product.type)
    if is_event:
        date = serialize(booking.stock.beginningDatetime)
    venue_departement_code = booking.stock.resolvedOffer.venue.departementCode
    response = {
        'bookingId': humanize(booking.id),
        'date': date,
        'email': booking.user.email,
        'isUsed': booking.isUsed,
        'offerName': offer_name,
        'userName': booking.user.publicName,
        'venueDepartementCode': venue_departement_code,
    }
    if product.type == str(EventType.ACTIVATION):
        response.update({'phoneNumber': booking.user.phoneNumber,
                         'dateOfBirth': serialize(booking.user.dateOfBirth)})

    return response
