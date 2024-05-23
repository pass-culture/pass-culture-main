from flask_login import current_user

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import validation as bookings_validation
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
from pcapi.models import api_errors
from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.booking_token import blueprint
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import login_or_api_key_required
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_cancel_booking
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_validate_booking
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings_v2

from . import serialization


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (None, "Authentification nécessaire"),
    "HTTP_403": (None, "Vous n'avez pas les droits nécessaires pour voir cette contremarque"),
    "HTTP_404": (None, "La contremarque n'existe pas"),
    "HTTP_410": (
        None,
        "Cette contremarque a été validée.\n En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé.",
    ),
}


def _get_booking_by_token_or_404(token: str) -> bookings_models.Booking:
    booking = bookings_models.Booking.query.filter_by(token=token.upper()).one_or_none()
    if not booking:
        errors = api_errors.ResourceNotFoundError()
        errors.add_error("global", "Cette contremarque n'a pas été trouvée")
        raise errors

    return booking


@blueprint.deprecated_booking_token_blueprint.route("/bookings/token/<token>", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.deprecated_public_api_schema,
    tags=[tags.DEPRECATED_BOOKING_TOKEN],
    deprecated=True,
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_200": (serialization.GetBookingResponse, "La contremarque existe et n’est pas validée"),
            }
        )
    ),
)
@login_or_api_key_required
def get_booking_by_token_v2(token: str) -> serialization.GetBookingResponse:
    # in French, to be used by Swagger for the API documentation
    """[Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations."""
    booking = _get_booking_by_token_or_404(token)

    if current_user.is_authenticated:
        # warning : current user is not none when user is not logged in
        check_user_can_validate_bookings_v2(current_user, booking.offererId)
    elif current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,
            booking.offererId,
        )
    else:
        # We should not end up here, thanks to the `login_or_api_key_required` decorator.
        raise ForbiddenError()

    bookings_validation.check_is_usable(booking)
    return serialization.get_booking_response(booking)


@blueprint.deprecated_booking_token_blueprint.route("/bookings/use/token/<token>", methods=["PATCH"])
@spectree_serialize(
    api=spectree_schemas.deprecated_public_api_schema,
    tags=[tags.DEPRECATED_BOOKING_TOKEN],
    on_success_status=204,
    deprecated=True,
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
    """[Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations."""
    booking = _get_booking_by_token_or_404(token)

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, booking.offererId)
    elif current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,
            booking.offererId,
        )
    else:
        # We should not end up here, thanks to the `login_or_api_key_required` decorator.
        raise ForbiddenError()

    bookings_api.mark_as_used(booking, bookings_models.BookingValidationAuthorType.OFFERER)


@blueprint.deprecated_booking_token_blueprint.route("/bookings/cancel/token/<token>", methods=["PATCH"])
@spectree_serialize(
    api=spectree_schemas.deprecated_public_api_schema,
    tags=[tags.DEPRECATED_BOOKING_TOKEN],
    on_success_status=204,
    deprecated=True,
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
@login_or_api_key_required
def patch_cancel_booking_by_token(token: str) -> None:
    # in French, to be used by Swagger for the API documentation
    """[Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations."""
    token = token.upper()
    booking = _get_booking_by_token_or_404(token)

    if current_user.is_authenticated:
        check_user_has_access_to_offerer(current_user, booking.offererId)
    elif current_api_key:
        check_api_key_allows_to_cancel_booking(
            current_api_key,
            booking.offererId,
        )
    else:
        # We should not end up here, thanks to the `login_or_api_key_required` decorator.
        raise ForbiddenError()

    try:
        bookings_api.cancel_booking_by_offerer(booking)
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"global": ["Cette contremarque a déjà été annulée"]})
    except (exceptions.BookingIsAlreadyRefunded, exceptions.BookingIsAlreadyUsed):
        raise api_errors.ForbiddenError({"global": ["Impossible d'annuler une réservation consommée"]})
    except external_bookings_exceptions.ExternalBookingException:
        raise api_errors.ApiErrors({"global": ["L'annulation de réservation a échoué."]})


@blueprint.deprecated_booking_token_blueprint.route("/bookings/keep/token/<token>", methods=["PATCH"])
@spectree_serialize(
    api=spectree_schemas.deprecated_public_api_schema,
    tags=[tags.DEPRECATED_BOOKING_TOKEN],
    deprecated=True,
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
@login_or_api_key_required
def patch_booking_keep_by_token(token: str) -> None:
    # in French, to be used by Swagger for the API documentation
    """[Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations."""
    booking = _get_booking_by_token_or_404(token)

    if current_user.is_authenticated:
        check_user_can_validate_bookings_v2(current_user, booking.offererId)
    elif current_api_key:
        check_api_key_allows_to_validate_booking(
            current_api_key,
            booking.offererId,
        )
    else:
        # We should not end up here, thanks to the `login_or_api_key_required` decorator.
        raise ForbiddenError()

    try:
        bookings_api.mark_as_unused(booking)
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"booking": ["Cette réservation a été annulée"]})
    except exceptions.BookingIsNotUsed:
        raise api_errors.ResourceGoneError({"booking": ["Cette réservation n'a pas encore été validée"]})
    except exceptions.BookingHasActivationCode:
        raise api_errors.ForbiddenError({"booking": ["Cette réservation ne peut pas être marquée comme inutilisée"]})
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ResourceGoneError({"payment": ["Le remboursement est en cours de traitement"]})
