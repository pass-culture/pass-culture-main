from datetime import datetime
from typing import Dict
from typing import Union

from flask import current_app as app
from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required
from spectree import Response

import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.models import Booking
import pcapi.core.bookings.repository as booking_repository
import pcapi.core.bookings.validation as bookings_validation
from pcapi.domain.user_activation import create_initial_deposit
from pcapi.domain.user_activation import is_activation_booking
from pcapi.domain.user_emails import send_activation_email
from pcapi.domain.users import check_is_authorized_to_access_bookings_recap
from pcapi.flask_app import private_api
from pcapi.flask_app import public_api
from pcapi.infrastructure.container import get_bookings_for_beneficiary
from pcapi.models import ApiKey
from pcapi.models import EventType
from pcapi.models import Recommendation
from pcapi.models import RightsType
from pcapi.models import StockSQLEntity
from pcapi.models import UserSQLEntity
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_type import ProductType
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository.api_key_queries import find_api_key_by_value
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization import serialize
from pcapi.routes.serialization import serialize_booking
from pcapi.routes.serialization.beneficiary_bookings_serialize import serialize_beneficiary_bookings
from pcapi.routes.serialization.bookings_recap_serialize import serialize_bookings_recap_paginated
from pcapi.routes.serialization.bookings_serialize import PostBookingBodyModel
from pcapi.routes.serialization.bookings_serialize import PostBookingResponseModel
from pcapi.routes.serialization.bookings_serialize import serialize_booking_minimal
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize
from pcapi.utils.includes import WEBAPP_GET_BOOKING_INCLUDES
from pcapi.utils.mailing import send_raw_email
from pcapi.utils.rest import ensure_current_user_has_rights
from pcapi.utils.rest import expect_json_data
from pcapi.validation.routes.bookings import check_email_and_offer_id_for_anonymous_user
from pcapi.validation.routes.bookings import check_page_format_is_number
from pcapi.validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided
from pcapi.validation.routes.users_authentifications import login_or_api_key_required_v2
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_cancel_booking
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_validate_booking
from pcapi.validation.routes.users_authorizations import check_user_can_validate_activation_offer
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings_v2


@private_api.route("/bookings/pro", methods=["GET"])
@login_required
def get_all_bookings():
    page = request.args.get("page", 1)
    check_page_format_is_number(page)

    check_is_authorized_to_access_bookings_recap(current_user)

    # FIXME: rewrite this route. The repository function should return
    # a bare SQLAlchemy query, and the route should handle the
    # serialization so that we can get rid of BookingsRecapPaginated
    # that is only used here.
    bookings_recap_paginated = booking_repository.find_by_pro_user_id(user_id=current_user.id, page=int(page))

    return serialize_bookings_recap_paginated(bookings_recap_paginated), 200


@private_api.route("/bookings", methods=["GET"])
@login_required
def get_bookings():
    beneficiary_bookings = get_bookings_for_beneficiary.execute(current_user.id)
    serialize_with_qr_code = True if feature_queries.is_active(FeatureToggle.QR_CODE) else False
    serialized_bookings = serialize_beneficiary_bookings(beneficiary_bookings, with_qr_code=serialize_with_qr_code)
    return jsonify(serialized_bookings), 200


@private_api.route("/bookings/<booking_id>", methods=["GET"])
@login_required
def get_booking(booking_id: int):
    booking = Booking.query.filter_by(id=dehumanize(booking_id)).first_or_404()

    return jsonify(as_dict(booking, includes=WEBAPP_GET_BOOKING_INCLUDES)), 200


@private_api.route("/bookings", methods=["POST"])
@login_required
@expect_json_data
@spectree_serialize(response_model=PostBookingResponseModel, on_success_status=201)
def create_booking(body: PostBookingBodyModel) -> PostBookingResponseModel:
    stock = StockSQLEntity.query.filter_by(id=dehumanize(body.stock_id)).first_or_404() if body.stock_id else None
    recommendation = (
        Recommendation.query.filter_by(id=dehumanize(body.recommendation_id)).first_or_404()
        if body.recommendation_id
        else None
    )

    booking = bookings_api.book_offer(
        beneficiary=current_user,
        stock=stock,
        quantity=body.quantity,
        recommendation=recommendation,
    )

    return PostBookingResponseModel(**serialize_booking_minimal(booking))


@private_api.route("/bookings/<booking_id>/cancel", methods=["PUT"])
@login_required
def cancel_booking(booking_id: str):
    booking = Booking.query.filter_by(id=dehumanize(booking_id)).first_or_404()

    bookings_api.cancel_booking_by_beneficiary(current_user, booking)

    return jsonify(serialize_booking_minimal(booking)), 200


@public_api.route("/bookings/token/<token>", methods=["GET"])
def get_booking_by_token(token: str):
    email = request.args.get("email", None)
    offer_id = dehumanize(request.args.get("offer_id", None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking_token_upper_case = token.upper()
    booking = booking_repository.find_by(booking_token_upper_case, email, offer_id)
    bookings_validation.check_is_usable(booking)

    if check_user_can_validate_bookings(current_user, booking.stock.offer.venue.managingOffererId):
        response = _create_response_to_get_booking_by_token(booking)
        return jsonify(response), 200

    return "", 204


@public_api.route("/bookings/token/<token>", methods=["PATCH"])
def patch_booking_by_token(token: str):
    email = request.args.get("email", None)
    offer_id = dehumanize(request.args.get("offer_id", None))
    booking_token_upper_case = token.upper()
    booking = booking_repository.find_by(booking_token_upper_case, email, offer_id)

    if current_user.is_authenticated:
        ensure_current_user_has_rights(RightsType.editor, booking.stock.offer.venue.managingOffererId)
    else:
        check_email_and_offer_id_for_anonymous_user(email, offer_id)

    bookings_api.mark_as_used(booking)

    if is_activation_booking(booking):
        _activate_user(booking.user)
        send_activation_email(booking.user, send_raw_email)

    return "", 204


@public_api.route("/v2/bookings/token/<token>", methods=["GET"])
@login_or_api_key_required_v2
def get_booking_by_token_v2(token: str):
    valid_api_key = _get_api_key_from_header(request)
    booking_token_upper_case = token.upper()
    booking = booking_repository.find_by(token=booking_token_upper_case)
    offerer_id = booking.stock.offer.venue.managingOffererId

    if current_user.is_authenticated:
        # warning : current user is not none when user is not logged in
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if valid_api_key:
        check_api_key_allows_to_validate_booking(valid_api_key, offerer_id)

    bookings_validation.check_is_usable(booking)

    response = serialize_booking(booking)

    return jsonify(response), 200


@public_api.route("/v2/bookings/use/token/<token>", methods=["PATCH"])
@login_or_api_key_required_v2
def patch_booking_use_by_token(token: str):
    """Let a pro user mark a booking as used."""
    booking_token_upper_case = token.upper()
    booking = booking_repository.find_by(token=booking_token_upper_case)
    offerer_id = booking.stock.offer.venue.managingOffererId
    valid_api_key = _get_api_key_from_header(request)

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if valid_api_key:
        check_api_key_allows_to_validate_booking(valid_api_key, offerer_id)

    if is_activation_booking(booking):
        _activate_user(booking.user)
        send_activation_email(booking.user, send_raw_email)

    bookings_api.mark_as_used(booking)

    return "", 204


@private_api.route("/v2/bookings/cancel/token/<token>", methods=["PATCH"])
@login_or_api_key_required_v2
def patch_cancel_booking_by_token(token: str):
    """Let a pro user cancel a booking."""
    valid_api_key = _get_api_key_from_header(request)
    token = token.upper()
    booking = booking_repository.find_by(token=token)
    offerer_id = booking.stock.offer.venue.managingOffererId

    if current_user.is_authenticated:
        ensure_current_user_has_rights(RightsType.editor, offerer_id)

    if valid_api_key:
        check_api_key_allows_to_cancel_booking(valid_api_key, offerer_id)

    bookings_api.cancel_booking_by_offerer(booking)

    return "", 204


@public_api.route("/v2/bookings/keep/token/<token>", methods=["PATCH"])
@login_or_api_key_required_v2
def patch_booking_keep_by_token(token: str):
    """Let a pro user mark a booking as _not_ used."""
    booking = booking_repository.find_by(token=token.upper())
    offerer_id = booking.stock.offer.venue.managingOffererId
    valid_api_key = _get_api_key_from_header(request)

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if valid_api_key:
        check_api_key_allows_to_validate_booking(valid_api_key, offerer_id)

    bookings_api.mark_as_unused(booking)

    return "", 204


def _activate_user(user_to_activate: UserSQLEntity) -> None:
    check_user_can_validate_activation_offer(current_user)
    user_to_activate.canBookFreeOffers = True
    deposit = create_initial_deposit(user_to_activate)
    repository.save(deposit)


def _get_api_key_from_header(received_request: Dict) -> ApiKey:
    authorization_header = received_request.headers.get("Authorization", None)
    headers_contains_api_key_authorization = authorization_header and "Bearer" in authorization_header

    if headers_contains_api_key_authorization:
        app_authorization_api_key = authorization_header.replace("Bearer ", "")
    else:
        app_authorization_api_key = None

    return find_api_key_by_value(app_authorization_api_key)


def _create_response_to_get_booking_by_token(booking: Booking) -> Dict:
    offer_name = booking.stock.offer.product.name
    date = None
    offer = booking.stock.offer
    is_event = ProductType.is_event(offer.type)
    if is_event:
        date = serialize(booking.stock.beginningDatetime)
    venue_departement_code = offer.venue.departementCode
    response = {
        "bookingId": humanize(booking.id),
        "date": date,
        "email": booking.user.email,
        "isUsed": booking.isUsed,
        "offerName": offer_name,
        "userName": booking.user.publicName,
        "venueDepartementCode": venue_departement_code,
    }

    if offer.type == str(EventType.ACTIVATION):
        response.update({"phoneNumber": booking.user.phoneNumber, "dateOfBirth": serialize(booking.user.dateOfBirth)})

    return response
