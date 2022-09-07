from flask_login import current_user

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import repository as booking_repository
from pcapi.core.bookings import validation as bookings_validation
from pcapi.models import api_errors
from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization.bookings_serialize import GetBookingResponse
from pcapi.routes.serialization.bookings_serialize import get_booking_response
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.rate_limiting import basic_auth_rate_limiter
from pcapi.utils.rate_limiting import ip_rate_limiter
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import login_or_api_key_required
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_cancel_booking
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_validate_booking
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings_v2


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (None, "Authentification nécessaire"),
    "HTTP_403": (None, "Vous n'avez pas les droits nécessaires pour voir cette contremarque"),
    "HTTP_404": (None, "La contremarque n'existe pas"),
    "HTTP_410": (None, "La contremarque n'est plus valide car elle a déjà été validée ou a été annulée"),
}


@blueprint.pro_public_api_v2.route("/bookings/token/<token>", methods=["GET"])
@ip_rate_limiter(deduct_when=lambda response: response.status_code == 401)
@basic_auth_rate_limiter()
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
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
    elif current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,  # type: ignore[arg-type]
            booking.offererId,
        )
    else:
        # We should not end up here, thanks to the `login_or_api_key_required` decorator.
        raise ForbiddenError()

    bookings_validation.check_is_usable(booking)
    return get_booking_response(booking)


@blueprint.pro_public_api_v2.route("/bookings/use/token/<token>", methods=["PATCH"])
@ip_rate_limiter(deduct_when=lambda response: response.status_code == 401)
@basic_auth_rate_limiter()
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
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
    elif current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,  # type: ignore[arg-type]
            booking.offererId,
        )
    else:
        # We should not end up here, thanks to the `login_or_api_key_required` decorator.
        raise ForbiddenError()

    bookings_api.mark_as_used(booking)


@blueprint.pro_public_api_v2.route("/bookings/cancel/token/<token>", methods=["PATCH"])
@ip_rate_limiter(deduct_when=lambda response: response.status_code == 401)
@basic_auth_rate_limiter()
@login_or_api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
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
    elif current_api_key:
        check_api_key_allows_to_cancel_booking(
            current_api_key,  # type: ignore[arg-type]
            booking.offererId,
        )
    else:
        # We should not end up here, thanks to the `login_or_api_key_required` decorator.
        raise ForbiddenError()

    try:
        bookings_api.cancel_booking_by_offerer(booking)
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"global": ["Cette contremarque a déjà été annulée"]})
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ForbiddenError({"global": ["Impossible d'annuler une réservation consommée"]})


@blueprint.pro_public_api_v2.route("/bookings/keep/token/<token>", methods=["PATCH"])
@ip_rate_limiter(deduct_when=lambda response: response.status_code == 401)
@basic_auth_rate_limiter()
@login_or_api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
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
    elif current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,  # type: ignore[arg-type]
            booking.offererId,
        )
    else:
        # We should not end up here, thanks to the `login_or_api_key_required` decorator.
        raise ForbiddenError()

    bookings_api.mark_as_unused(booking)
