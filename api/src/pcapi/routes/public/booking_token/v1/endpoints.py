from flask import request
from flask_login import current_user

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as booking_repository
from pcapi.core.bookings import validation as bookings_validation
from pcapi.models import api_errors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.serialization import serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.validation.routes.bookings import check_email_and_offer_id_for_anonymous_user
from pcapi.validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings

from . import blueprint
from . import serialization


def _create_response_to_get_booking_by_token(booking: bookings_models.Booking) -> dict:
    offer_name = booking.stock.offer.product.name
    date = None
    offer = booking.stock.offer
    is_event = offer.isEvent
    if is_event:
        date = serialize(booking.stock.beginningDatetime)
    venue_departement_code = offer.venue.departementCode
    response = {
        "bookingId": humanize(booking.id),
        "date": date,
        "email": booking.email,
        "isUsed": booking.is_used_or_reimbursed,
        "offerName": offer_name,
        "userName": booking.userName,
        "venueDepartementCode": venue_departement_code,
    }

    return response


def _check_activation_of_this_api() -> None:
    if not FeatureToggle.WIP_ENABLE_API_CONTREMARQUE_V1.is_active():
        raise api_errors.ResourceNotFoundError(
            errors={
                "global": "La version 1 de l'API contremarque n'est plus disponible. Veuillez utiliser la version 2 de l'API ou le guichet de validation du portail pro."
            }
        )


# TODO (gvanneste, 2021-10-19) : retravailler cette fonction, notamment check_user_is_logged_in_or_email_is_provided
# À brûler : juste checker si le user a droit de récupérer les bookings
@blueprint.deprecated_booking_token_api.route("/bookings/token/<token>", methods=["GET"])
@spectree_serialize(
    response_model=serialization.LegacyBookingResponse,
    on_success_status=200,
    on_empty_status=204,
)
def get_booking_by_token(token: str) -> serialization.LegacyBookingResponse | None:
    _check_activation_of_this_api()
    email: str | None = request.args.get("email", None)
    offer_id = dehumanize(request.args.get("offer_id", None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking = booking_repository.find_by(token, email, offer_id)

    bookings_validation.check_is_usable(booking)

    if check_user_can_validate_bookings(current_user, booking.offererId):
        response = _create_response_to_get_booking_by_token(booking)
        return serialization.LegacyBookingResponse(**response)

    return None


@blueprint.deprecated_booking_token_api.route("/bookings/token/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204)
def patch_booking_by_token(token: str, query: serialization.PatchBookingByTokenQueryModel) -> None:
    _check_activation_of_this_api()
    email = query.email
    offer_id = dehumanize(query.offer_id)
    booking = booking_repository.find_by(token, email, offer_id)

    if current_user.is_authenticated:
        check_user_has_access_to_offerer(current_user, booking.offererId)
    else:
        check_email_and_offer_id_for_anonymous_user(email, offer_id)

    bookings_api.mark_as_used(booking)
