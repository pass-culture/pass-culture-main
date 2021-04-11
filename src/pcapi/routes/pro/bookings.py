from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required

import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.models import Booking
import pcapi.core.bookings.repository as booking_repository
import pcapi.core.bookings.validation as bookings_validation
from pcapi.domain.users import check_is_authorized_to_access_bookings_recap
from pcapi.flask_app import private_api
from pcapi.flask_app import public_api
from pcapi.models import EventType
from pcapi.models.offer_type import ProductType
from pcapi.routes.serialization import serialize
from pcapi.routes.serialization import serialize_booking
from pcapi.routes.serialization.bookings_recap_serialize import serialize_bookings_recap_paginated
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.validation.routes.bookings import check_email_and_offer_id_for_anonymous_user
from pcapi.validation.routes.bookings import check_page_format_is_number
from pcapi.validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import login_or_api_key_required
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_cancel_booking
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_validate_booking
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings_v2


# @debt api-migration
@public_api.route("/bookings/token/<token>", methods=["GET"])
def get_booking_by_token(token: str):
    email = request.args.get("email", None)
    offer_id = dehumanize(request.args.get("offer_id", None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking = booking_repository.find_by(token, email, offer_id)
    bookings_validation.check_is_usable(booking)

    if check_user_can_validate_bookings(current_user, booking.stock.offer.venue.managingOffererId):
        response = _create_response_to_get_booking_by_token(booking)
        return jsonify(response), 200

    return "", 204


# @debt api-migration
@public_api.route("/bookings/token/<token>", methods=["PATCH"])
def patch_booking_by_token(token: str):
    email = request.args.get("email", None)
    offer_id = dehumanize(request.args.get("offer_id", None))
    booking = booking_repository.find_by(token, email, offer_id)

    if current_user.is_authenticated:
        check_user_has_access_to_offerer(current_user, booking.stock.offer.venue.managingOffererId)
    else:
        check_email_and_offer_id_for_anonymous_user(email, offer_id)

    bookings_api.mark_as_used(booking)

    return "", 204


# @debt api-migration
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


# @debt api-migration
@public_api.route("/v2/bookings/token/<token>", methods=["GET"])
@login_or_api_key_required
def get_booking_by_token_v2(token: str):
    booking = booking_repository.find_by(token=token)
    offerer_id = booking.stock.offer.venue.managingOffererId

    if current_user.is_authenticated:
        # warning : current user is not none when user is not logged in
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if current_api_key:
        check_api_key_allows_to_validate_booking(current_api_key, offerer_id)

    bookings_validation.check_is_usable(booking)

    response = serialize_booking(booking)

    return jsonify(response), 200


# @debt api-migration
@public_api.route("/v2/bookings/use/token/<token>", methods=["PATCH"])
@login_or_api_key_required
def patch_booking_use_by_token(token: str):
    """Let a pro user mark a booking as used."""
    booking = booking_repository.find_by(token=token)
    offerer_id = booking.stock.offer.venue.managingOffererId

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if current_api_key:
        check_api_key_allows_to_validate_booking(current_api_key, offerer_id)

    bookings_api.mark_as_used(booking)

    return "", 204


# @debt api-migration
@private_api.route("/v2/bookings/cancel/token/<token>", methods=["PATCH"])
@login_or_api_key_required
def patch_cancel_booking_by_token(token: str):
    """Let a pro user cancel a booking."""
    token = token.upper()
    booking = booking_repository.find_by(token=token)
    offerer_id = booking.stock.offer.venue.managingOffererId

    if current_user.is_authenticated:
        check_user_has_access_to_offerer(current_user, offerer_id)

    if current_api_key:
        check_api_key_allows_to_cancel_booking(current_api_key, offerer_id)

    bookings_api.cancel_booking_by_offerer(booking)

    return "", 204


# @debt api-migration
@public_api.route("/v2/bookings/keep/token/<token>", methods=["PATCH"])
@login_or_api_key_required
def patch_booking_keep_by_token(token: str):
    """Let a pro user mark a booking as _not_ used."""
    booking = booking_repository.find_by(token=token)
    offerer_id = booking.stock.offer.venue.managingOffererId

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, offerer_id)

    if current_api_key:
        check_api_key_allows_to_validate_booking(current_api_key, offerer_id)

    bookings_api.mark_as_unused(booking)

    return "", 204


def _create_response_to_get_booking_by_token(booking: Booking) -> dict:
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
