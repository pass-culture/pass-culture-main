from typing import Optional

from flask import request
from flask_login import current_user
from flask_login import login_required

import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.models import Booking
import pcapi.core.bookings.repository as booking_repository
import pcapi.core.bookings.validation as bookings_validation
from pcapi.routes.serialization import serialize
from pcapi.routes.serialization.bookings_recap_serialize import ListBookingsQueryModel
from pcapi.routes.serialization.bookings_recap_serialize import ListBookingsResponseModel
from pcapi.routes.serialization.bookings_recap_serialize import PatchBookingByTokenQueryModel
from pcapi.routes.serialization.bookings_recap_serialize import _serialize_booking_recap
from pcapi.routes.serialization.bookings_serialize import GetBookingResponse
from pcapi.routes.serialization.bookings_serialize import LegacyBookingResponse
from pcapi.routes.serialization.bookings_serialize import UserHasBookingResponse
from pcapi.routes.serialization.bookings_serialize import get_booking_response
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize
from pcapi.utils.rate_limiting import basic_auth_rate_limiter
from pcapi.utils.rate_limiting import ip_rate_limiter
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.validation.routes.bookings import check_email_and_offer_id_for_anonymous_user
from pcapi.validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import login_or_api_key_required
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_cancel_booking
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_validate_booking
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings_v2

from . import blueprint


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (None, "Authentification nécessaire"),
    "HTTP_403": (None, "Vous n'avez pas les droits nécessaires pour voir cette contremarque"),
    "HTTP_404": (None, "La contremarque n'existe pas"),
    "HTTP_410": (None, "La contremarque n'est plus valide car elle a déjà été validée ou a été annulée"),
}

# TODO (gvanneste, 2021-10-19) : retravailler cette fonction, notamment check_user_is_logged_in_or_email_is_provided
# À brûler : juste checker si le user a droit de récupérer les bookings
@blueprint.pro_public_api_v1.route("/bookings/token/<token>", methods=["GET"])
@spectree_serialize(
    response_model=LegacyBookingResponse,
    on_success_status=200,
    on_empty_status=204,
)
def get_booking_by_token(token: str) -> Optional[LegacyBookingResponse]:
    email: Optional[str] = request.args.get("email", None)
    offer_id = dehumanize(request.args.get("offer_id", None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking = booking_repository.find_by(token, email, offer_id)
    bookings_validation.check_is_usable(booking)

    if check_user_can_validate_bookings(current_user, booking.offererId):
        response = _create_response_to_get_booking_by_token(booking)
        return LegacyBookingResponse(**response)

    return None


@blueprint.pro_public_api_v1.route("/bookings/token/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204)
def patch_booking_by_token(token: str, query: PatchBookingByTokenQueryModel) -> None:
    email = query.email
    offer_id = dehumanize(query.offer_id)
    booking = booking_repository.find_by(token, email, offer_id)

    if current_user.is_authenticated:
        check_user_has_access_to_offerer(current_user, booking.offererId)
    else:
        check_email_and_offer_id_for_anonymous_user(email, offer_id)

    bookings_api.mark_as_used(booking)


@blueprint.pro_private_api.route("/bookings/pro", methods=["GET"])
@login_required
@spectree_serialize(response_model=ListBookingsResponseModel)
def get_bookings_pro(query: ListBookingsQueryModel) -> ListBookingsResponseModel:
    page = query.page
    venue_id = query.venue_id
    event_date = query.event_date
    booking_status = query.booking_status_filter
    booking_period = (query.booking_period_beginning_date, query.booking_period_ending_date)
    offer_type = query.offer_type

    # FIXME: rewrite this route. The repository function should return
    # a bare SQLAlchemy query, and the route should handle the
    # serialization so that we can get rid of BookingsRecapPaginated
    # that is only used here.
    bookings_recap_paginated = booking_repository.find_by_pro_user(
        user=current_user._get_current_object(),  # for tests to succeed, because current_user is actually a LocalProxy
        booking_period=booking_period,
        status_filter=booking_status,
        event_date=event_date,
        venue_id=venue_id,
        offer_type=offer_type,
        page=int(page),
    )

    return ListBookingsResponseModel(
        bookings_recap=[
            _serialize_booking_recap(booking_recap) for booking_recap in bookings_recap_paginated.bookings_recap
        ],
        page=bookings_recap_paginated.page,
        pages=bookings_recap_paginated.pages,
        total=bookings_recap_paginated.total,
    )


@blueprint.pro_private_api.route("/bookings/pro/userHasBookings", methods=["GET"])
@login_required
@spectree_serialize(response_model=UserHasBookingResponse)
def get_user_has_bookings() -> UserHasBookingResponse:
    user = current_user._get_current_object()
    return UserHasBookingResponse(hasBookings=booking_repository.user_has_bookings(user))


@blueprint.pro_private_api.route("/bookings/csv", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8;",
        "Content-Disposition": "attachment; filename=reservations_pass_culture.csv",
    },
)
def get_bookings_csv(query: ListBookingsQueryModel) -> bytes:
    venue_id = query.venue_id
    event_date = query.event_date
    booking_period = (query.booking_period_beginning_date, query.booking_period_ending_date)
    booking_status = query.booking_status_filter
    offer_type = query.offer_type

    bookings = booking_repository.get_csv_report(
        user=current_user._get_current_object(),  # for tests to succeed, because current_user is actually a LocalProxy
        booking_period=booking_period,
        status_filter=booking_status,
        event_date=event_date,
        venue_id=venue_id,
        offer_type=offer_type,
    )

    return bookings.encode("utf-8-sig")


@blueprint.pro_public_api_v2.route("/bookings/token/<token>", methods=["GET"])
@ip_rate_limiter(deduct_when=lambda response: response.status_code == 401)
@basic_auth_rate_limiter()
@spectree_serialize(
    api=blueprint.api_v2,
    tags=["API Contremarque"],
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_200": (GetBookingResponse, "La contremarque existe et n’est pas validée"),
            }
        )
    ),
)
@login_or_api_key_required
def get_booking_by_token_v2(token: str) -> GetBookingResponse:
    # in French, to be used by Swagger for the API documentation
    """Consultation d'une réservation.

    Le code “contremarque” ou "token" est une chaîne de caractères permettant d’identifier la réservation et qui sert de preuve de réservation.
    Ce code unique est généré pour chaque réservation d'un utilisateur sur l'application et lui est transmis à cette occasion.
    """
    booking = booking_repository.find_by(token=token)

    if current_user.is_authenticated:
        # warning : current user is not none when user is not logged in
        check_user_can_validate_bookings_v2(current_user, booking.offererId)

    if current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,  # type: ignore[arg-type]
            booking.offererId,
        )

    bookings_validation.check_is_usable(booking)

    return get_booking_response(booking)


@blueprint.pro_public_api_v2.route("/bookings/use/token/<token>", methods=["PATCH"])
@ip_rate_limiter(deduct_when=lambda response: response.status_code == 401)
@basic_auth_rate_limiter()
@spectree_serialize(
    api=blueprint.api_v2,
    tags=["API Contremarque"],
    on_success_status=204,
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_204": (None, "La contremarque a bien été validée"),
            }
        )
    ),
)
@login_or_api_key_required
def patch_booking_use_by_token(token: str) -> None:
    # in French, to be used by Swagger for the API documentation
    """Validation d'une réservation.

    Pour confirmer que la réservation a bien été utilisée par le jeune.
    """
    booking = booking_repository.find_by(token=token)

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, booking.offererId)

    if current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,  # type: ignore[arg-type]
            booking.offererId,
        )

    bookings_api.mark_as_used(booking)


@blueprint.pro_public_api_v2.route("/bookings/cancel/token/<token>", methods=["PATCH"])
@ip_rate_limiter(deduct_when=lambda response: response.status_code == 401)
@basic_auth_rate_limiter()
@login_or_api_key_required
@spectree_serialize(
    api=blueprint.api_v2,
    tags=["API Contremarque"],
    on_success_status=204,
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_204": (None, "La contremarque a été annulée avec succès"),
                "HTTP_403": (
                    None,
                    "Vous n'avez pas les droits nécessaires pour annuler cette contremarque ou la réservation a déjà été validée",
                ),
                "HTTP_410": (None, "La contremarque a déjà été annulée"),
            }
        )
    ),
)
def patch_cancel_booking_by_token(token: str) -> None:
    # in French, to be used by Swagger for the API documentation
    """Annulation d'une réservation.

    Bien que, dans le cas d’un événement, l’utilisateur ne peut plus annuler sa réservation 72h avant le début de ce dernier,
    cette API permet d’annuler la réservation d’un utilisateur si elle n’a pas encore été validé.
    """
    token = token.upper()
    booking = booking_repository.find_by(token=token)

    if current_user.is_authenticated:
        check_user_has_access_to_offerer(current_user, booking.offererId)

    if current_api_key:
        check_api_key_allows_to_cancel_booking(
            current_api_key,  # type: ignore[arg-type]
            booking.offererId,
        )

    bookings_api.cancel_booking_by_offerer(booking)


@blueprint.pro_public_api_v2.route("/bookings/keep/token/<token>", methods=["PATCH"])
@ip_rate_limiter(deduct_when=lambda response: response.status_code == 401)
@basic_auth_rate_limiter()
@login_or_api_key_required
@spectree_serialize(
    api=blueprint.api_v2,
    tags=["API Contremarque"],
    on_success_status=204,
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_204": (None, "L'annulation de la validation de la contremarque a bien été effectuée"),
                "HTTP_410": (
                    None,
                    "La requête est refusée car la contremarque n'a pas encore été validée, a été annulée, ou son remboursement a été initié",
                ),
            }
        )
    ),
)
def patch_booking_keep_by_token(token: str) -> None:
    # in French, to be used by Swagger for the API documentation
    """Annulation de la validation d'une réservation."""
    booking = booking_repository.find_by(token=token)

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, booking.offererId)

    if current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,  # type: ignore[arg-type]
            booking.offererId,
        )

    bookings_api.mark_as_unused(booking)


def _create_response_to_get_booking_by_token(booking: Booking) -> dict:
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
