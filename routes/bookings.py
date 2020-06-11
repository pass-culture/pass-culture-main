from datetime import datetime
from typing import Union, Dict

from flask import current_app as app
from flask import jsonify, request
from flask_login import current_user, login_required

from connectors import redis
from domain.user_activation import create_initial_deposit, is_activation_booking
from domain.user_emails import send_activation_email, \
    send_booking_cancellation_emails_to_user_and_offerer
from infrastructure.container import book_an_offer
from models import BookingSQLEntity, EventType, RightsType, ApiKey, UserSQLEntity
from models.feature import FeatureToggle
from models.offer_type import ProductType
from repository import booking_queries, feature_queries, repository
from repository.api_key_queries import find_api_key_by_value
from routes.serialization import as_dict, serialize, serialize_booking
from routes.serialization.bookings_recap_serialize import serialize_bookings_recap_paginated
from routes.serialization.bookings_serialize import serialize_booking_for_book_an_offer
from use_cases.book_an_offer import BookingInformation
from use_cases.cancel_a_booking import CancelABooking
from use_cases.get_all_bookings_by_pro_user import get_all_bookings_by_pro_user
from utils.human_ids import dehumanize, humanize
from utils.includes import WEBAPP_GET_BOOKING_INCLUDES, \
    WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES, \
    WEBAPP_PATCH_POST_BOOKING_INCLUDES
from utils.mailing import MailServiceException, send_raw_email
from utils.rest import ensure_current_user_has_rights, expect_json_data
from validation.routes.bookings import check_booking_is_cancellable_by_user, \
    check_booking_is_not_already_cancelled, \
    check_booking_is_not_used, \
    check_booking_token_is_keepable, \
    check_booking_token_is_usable, \
    check_email_and_offer_id_for_anonymous_user, \
    check_has_stock_id, \
    check_is_not_activation_booking, \
    check_page_format_is_number
from validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided, \
    login_or_api_key_required_v2
from validation.routes.users_authorizations import \
    check_api_key_allows_to_cancel_booking, \
    check_api_key_allows_to_validate_booking, check_user_can_validate_activation_offer, \
    check_user_can_validate_bookings, \
    check_user_can_validate_bookings_v2, check_user_can_cancel_booking_by_id


@app.route('/bookings/pro', methods=['GET'])
@login_required
def get_all_bookings():
    page = request.args.get('page', 1)
    check_page_format_is_number(page)
    bookings_recap_paginated = get_all_bookings_by_pro_user(user_id=current_user.id, page=int(page))

    return serialize_bookings_recap_paginated(bookings_recap_paginated), 200


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
    booking = BookingSQLEntity.query.filter_by(id=dehumanize(booking_id)).first_or_404()

    return jsonify(as_dict(booking, includes=WEBAPP_GET_BOOKING_INCLUDES)), 200


@app.route('/bookings', methods=['POST'])
@login_required
@expect_json_data
def create_booking():
    stock_id = request.json.get('stockId')
    recommendation_id = request.json.get('recommendationId')
    quantity = request.json.get('quantity')
    check_has_stock_id(stock_id)

    booking_information = BookingInformation(
        dehumanize(stock_id),
        current_user.id,
        quantity,
        dehumanize(recommendation_id)
    )

    created_booking = book_an_offer.execute(booking_information)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=created_booking.stock.offer.id)

    return jsonify(serialize_booking_for_book_an_offer(created_booking)), 201


@app.route('/bookings/<booking_id>/cancel', methods=['PUT'])
@login_required
def cancel_booking(booking_id: str):
    dehumanized_booking_id = dehumanize(booking_id)
    cancel_a_booking = CancelABooking()
    booking = cancel_a_booking.execute(booking_id=dehumanized_booking_id, current_user=current_user)

    if booking.isCancelled:
        return '', 204

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=booking.stock.offerId)

    return jsonify(as_dict(booking, includes=WEBAPP_PATCH_POST_BOOKING_INCLUDES)), 200


@app.route('/bookings/token/<token>', methods=['GET'])
def get_booking_by_token(token: str):
    email = request.args.get('email', None)
    offer_id = dehumanize(request.args.get('offer_id', None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking_token_upper_case = token.upper()
    booking = booking_queries.find_by(booking_token_upper_case, email, offer_id)
    check_booking_token_is_usable(booking)

    offerer_id = booking.stock.offer.venue.managingOffererId

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
    offerer_id = booking.stock.offer.venue.managingOffererId

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
            RightsType.editor, booking.stock.offer.venue.managingOffererId)
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
    offerer_id = booking.stock.offer.venue.managingOffererId
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
    offerer_id = booking.stock.offer.venue.managingOffererId

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
    offerer_id = booking.stock.offer.venue.managingOffererId
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


def _activate_user(user_to_activate: UserSQLEntity) -> None:
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


def _create_response_to_get_booking_by_token(booking: BookingSQLEntity) -> Dict:
    offer_name = booking.stock.offer.product.name
    date = None
    offer = booking.stock.offer
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
