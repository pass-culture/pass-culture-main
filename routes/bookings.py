from datetime import datetime
from itertools import chain
from typing import Union, Dict

import dateutil
from flask import current_app as app
from flask import jsonify, request
from flask_login import current_user, login_required

from connectors import redis
from domain.bookings import generate_bookings_details_csv
from domain.expenses import get_expenses
from domain.user_activation import create_initial_deposit, is_activation_booking
from domain.user_emails import send_activation_email, \
    send_booking_confirmation_email_to_beneficiary, \
    send_booking_recap_emails, send_booking_cancellation_emails_to_user_and_offerer
from models import ApiErrors, Booking, EventType, Offerer, RightsType, Stock, ApiKey, User
from models.feature import FeatureToggle
from models.offer_type import ProductType
from repository import booking_queries, feature_queries, repository
from repository.api_key_queries import find_api_key_by_value
from repository.user_offerer_queries import \
    filter_query_where_user_is_user_offerer_and_is_validated
from routes.serialization import as_dict, serialize, serialize_booking
from utils.human_ids import dehumanize, humanize
from utils.includes import WEBAPP_GET_BOOKING_INCLUDES, \
    WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES, \
    WEBAPP_PATCH_POST_BOOKING_INCLUDES
from utils.mailing import MailServiceException, send_raw_email
from utils.rest import ensure_current_user_has_rights, expect_json_data
from utils.token import random_token
from validation.routes.bookings import check_already_booked, \
    check_booking_is_cancellable_by_user, \
    check_booking_is_not_already_cancelled, \
    check_booking_is_not_used, \
    check_quantity_is_valid, \
    check_booking_token_is_keepable, \
    check_booking_token_is_usable, \
    check_email_and_offer_id_for_anonymous_user, \
    check_existing_stock, check_expenses_limits, \
    check_has_stock_id, \
    check_is_not_activation_booking, \
    check_not_soft_deleted_stock, \
    check_offer_date, check_offer_is_active, \
    check_rights_to_get_bookings_csv, \
    check_stock_booking_limit_date, \
    check_stock_venue_is_validated, check_stock_is_bookable
from validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided, \
    login_or_api_key_required_v2
from validation.routes.users_authorizations import \
    check_api_key_allows_to_cancel_booking, \
    check_api_key_allows_to_validate_booking, check_can_book_free_offer, \
    check_user_can_validate_activation_offer, check_user_can_validate_bookings, \
    check_user_can_validate_bookings_v2, check_user_can_cancel_booking_by_id


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
    bookings = chain(*list(map(lambda offerer: booking_queries.find_all_bookings_info(offerer.id,
                                                                                      venue_id,
                                                                                      offer_id,
                                                                                      date_from,
                                                                                      date_to,
                                                                                      only_digital_venues),
                               query)))

    bookings_csv = generate_bookings_details_csv(bookings)

    return bookings_csv.encode('utf-8-sig'), \
           200, \
           {'Content-type': 'text/csv; charset=utf-8;',
            'Content-Disposition': 'attachment; filename=reservations_pass_culture.csv'}


@app.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    bookings = booking_queries.find_for_my_bookings_page(current_user.id)

    if feature_queries.is_active(FeatureToggle.QR_CODE):
        includes = WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES
    else:
        includes = WEBAPP_GET_BOOKING_INCLUDES

    return jsonify([as_dict(b, includes=includes) for b in bookings]), 200


@app.route('/bookings/<booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id: int):
    booking = Booking.query.filter_by(id=dehumanize(booking_id)).first_or_404()

    return jsonify(as_dict(booking, includes=WEBAPP_GET_BOOKING_INCLUDES)), 200


@app.route('/bookings', methods=['POST'])
@login_required
@expect_json_data
def create_booking():
    stock_id = request.json.get('stockId')
    recommendation_id = request.json.get('recommendationId')
    quantity = request.json.get('quantity')
    check_has_stock_id(stock_id)
    stock = Stock.query.filter_by(id=dehumanize(stock_id)).first()
    check_existing_stock(stock)

    stock_already_booked_by_user = booking_queries.is_stock_already_booked_by_user(stock, current_user)
    check_already_booked(stock_already_booked_by_user)

    offer_is_duo = stock.offer.isDuo
    check_quantity_is_valid(quantity, offer_is_duo)

    check_can_book_free_offer(stock, current_user)

    check_stock_is_bookable(stock)

    new_booking = Booking(from_dict={
        'stockId': stock_id,
        'amount': stock.price,
        'token': random_token(),
        'userId': humanize(current_user.id),
        'quantity': quantity,
        'recommendationId': recommendation_id if recommendation_id else None
    })

    bookings = booking_queries.find_active_bookings_by_user_id(current_user.id)
    expenses = get_expenses(bookings)
    check_expenses_limits(expenses, new_booking, stock)
    repository.save(new_booking)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    try:
        send_booking_recap_emails(new_booking, send_raw_email)
    except MailServiceException as error:
        app.logger.error('Mail service failure', error)

    try:
        send_booking_confirmation_email_to_beneficiary(new_booking, send_raw_email)
    except MailServiceException as error:
        app.logger.error('Mail service failure', error)

    return jsonify(as_dict(new_booking, includes=WEBAPP_PATCH_POST_BOOKING_INCLUDES)), 201


@app.route('/bookings/<booking_id>/cancel', methods=['PUT'])
@login_required
def cancel_booking(booking_id: int):
    booking = booking_queries.find_by_id(dehumanize(booking_id))
    booking_offerer = booking.stock.resolvedOffer.venue.managingOffererId

    is_offerer_cancellation = current_user.hasRights(
        RightsType.editor, booking_offerer)
    is_user_cancellation = booking.user == current_user

    check_user_can_cancel_booking_by_id(is_user_cancellation, is_offerer_cancellation)

    if is_user_cancellation:
        check_booking_is_cancellable_by_user(booking, is_user_cancellation)

    if booking.isCancelled:
        return '', 204

    booking.isCancelled = True
    repository.save(booking)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=booking.stock.offerId)

    try:
        send_booking_cancellation_emails_to_user_and_offerer(booking, is_offerer_cancellation, is_user_cancellation,
                                                             send_raw_email)
    except MailServiceException as error:
        app.logger.error('Mail service failure', error)

    return jsonify(as_dict(booking, includes=WEBAPP_PATCH_POST_BOOKING_INCLUDES)), 200


@app.route('/bookings/token/<token>', methods=['GET'])
def get_booking_by_token(token: str):
    email = request.args.get('email', None)
    offer_id = dehumanize(request.args.get('offer_id', None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking_token_upper_case = token.upper()
    booking = booking_queries.find_by(booking_token_upper_case, email, offer_id)
    check_booking_token_is_usable(booking)

    offerer_id = booking.stock.resolvedOffer.venue.managingOffererId

    current_user_can_validate_booking = check_user_can_validate_bookings(current_user, offerer_id)

    if current_user_can_validate_booking:
        response = _create_response_to_get_booking_by_token(booking)
        return jsonify(response), 200

    return '', 204


@app.route('/v2/bookings/token/<token>', methods=['GET'])
@login_or_api_key_required_v2
def get_booking_by_token_v2(token: str):
    app_authorization_api_key = _extract_api_key_from_request(request)
    valid_api_key = find_api_key_by_value(app_authorization_api_key)
    booking_token_upper_case = token.upper()
    booking = booking_queries.find_by(booking_token_upper_case)
    offerer_id = booking.stock.resolvedOffer.venue.managingOffererId

    if current_user.is_authenticated:
        # warning : current user is not none when user is not logged in
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if valid_api_key:
        check_api_key_allows_to_validate_booking(valid_api_key, offerer_id)

    check_booking_token_is_usable(booking)

    response = serialize_booking(booking)

    return jsonify(response), 200


@app.route('/bookings/token/<token>', methods=['PATCH'])
def patch_booking_by_token(token: str):
    email = request.args.get('email', None)
    offer_id = dehumanize(request.args.get('offer_id', None))
    booking_token_upper_case = token.upper()
    booking = booking_queries.find_by(booking_token_upper_case, email, offer_id)

    if current_user.is_authenticated:
        ensure_current_user_has_rights(
            RightsType.editor, booking.stock.resolvedOffer.venue.managingOffererId)
    else:
        check_email_and_offer_id_for_anonymous_user(email, offer_id)

    check_booking_token_is_usable(booking)

    if is_activation_booking(booking):
        _activate_user(booking.user)
        send_activation_email(booking.user, send_raw_email)

    booking.isUsed = True
    booking.dateUsed = datetime.utcnow()
    repository.save(booking)

    return '', 204


@app.route('/v2/bookings/use/token/<token>', methods=['PATCH'])
@login_or_api_key_required_v2
def patch_booking_use_by_token(token: str):
    booking_token_upper_case = token.upper()
    booking = booking_queries.find_by(booking_token_upper_case)
    offerer_id = booking.stock.resolvedOffer.venue.managingOffererId
    valid_api_key = _get_api_key_from_header(request)

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if valid_api_key:
        check_api_key_allows_to_validate_booking(valid_api_key, offerer_id)

    if is_activation_booking(booking):
        _activate_user(booking.user)
        send_activation_email(booking.user, send_raw_email)

    check_booking_token_is_usable(booking)

    booking.isUsed = True
    booking.dateUsed = datetime.utcnow()

    repository.save(booking)

    return '', 204


@app.route('/v2/bookings/cancel/token/<token>', methods=['PATCH'])
@login_or_api_key_required_v2
def patch_cancel_booking_by_token(token: str):
    app_authorization_api_key = _extract_api_key_from_request(request)
    valid_api_key = find_api_key_by_value(app_authorization_api_key)
    token = token.upper()
    booking = booking_queries.find_by(token)
    offerer_id = booking.stock.resolvedOffer.venue.managingOffererId

    if current_user.is_authenticated:
        ensure_current_user_has_rights(RightsType.editor, offerer_id)

    if valid_api_key:
        check_api_key_allows_to_cancel_booking(valid_api_key, offerer_id)

    check_booking_is_not_already_cancelled(booking)
    check_booking_is_not_used(booking)

    booking.isCancelled = True
    repository.save(booking)

    return '', 204


@app.route('/v2/bookings/keep/token/<token>', methods=['PATCH'])
@login_or_api_key_required_v2
def patch_booking_keep_by_token(token: str):
    booking_token_upper_case = token.upper()
    booking = booking_queries.find_by(booking_token_upper_case)
    offerer_id = booking.stock.resolvedOffer.venue.managingOffererId
    valid_api_key = _get_api_key_from_header(request)

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if valid_api_key:
        check_api_key_allows_to_validate_booking(valid_api_key, offerer_id)

    check_is_not_activation_booking(booking)
    check_booking_token_is_keepable(booking)

    booking.isUsed = False
    booking.dateUsed = None

    repository.save(booking)

    return '', 204


def _activate_user(user_to_activate: User) -> None:
    check_user_can_validate_activation_offer(current_user)
    user_to_activate.canBookFreeOffers = True
    deposit = create_initial_deposit(user_to_activate)
    repository.save(deposit)


def _extract_api_key_from_request(received_request: Dict) -> Union[str, None]:
    authorization_header = received_request.headers.get('Authorization', None)
    headers_contains_api_key_authorization = authorization_header and 'Bearer' in authorization_header

    if headers_contains_api_key_authorization:
        return authorization_header.replace('Bearer ', '')
    else:
        return None


def _get_api_key_from_header(received_request: Dict) -> ApiKey:
    authorization_header = received_request.headers.get('Authorization', None)
    headers_contains_api_key_authorization = authorization_header and 'Bearer' in authorization_header

    if headers_contains_api_key_authorization:
        app_authorization_api_key = authorization_header.replace('Bearer ', '')
    else:
        app_authorization_api_key = None

    return find_api_key_by_value(app_authorization_api_key)


def _create_response_to_get_booking_by_token(booking: Booking) -> Dict:
    offer_name = booking.stock.resolvedOffer.product.name
    date = None
    offer = booking.stock.resolvedOffer
    is_event = ProductType.is_event(offer.type)
    if is_event:
        date = serialize(booking.stock.beginningDatetime)
    venue_departement_code = offer.venue.departementCode
    response = {
        'bookingId': humanize(booking.id),
        'date': date,
        'email': booking.user.email,
        'isUsed': booking.isUsed,
        'offerName': offer_name,
        'userName': booking.user.publicName,
        'venueDepartementCode': venue_departement_code,
    }

    if offer.type == str(EventType.ACTIVATION):
        response.update({'phoneNumber': booking.user.phoneNumber,
                         'dateOfBirth': serialize(booking.user.dateOfBirth)})

    return response
