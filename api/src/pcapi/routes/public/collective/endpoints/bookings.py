import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models
from pcapi.core.educational.api import booking as educational_api_booking
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.models as providers_models
from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required


@blueprints.public_api.route("/v2/collective/bookings/<int:booking_id>", methods=["PATCH"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_BOOKINGS],
    on_success_status=204,
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_COLLECTIVE_BOOKING_CANCELLATION_SUCCESS
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
        )
    ),
)
def cancel_collective_booking(booking_id: int) -> None:
    """
    Cancel Collective Booking

    Cancel a collective event booking.
    """
    booking = _get_booking(booking_id)
    if not booking:
        raise NotFound()

    try:
        reason = models.CollectiveBookingCancellationReasons.PUBLIC_API
        educational_api_booking.cancel_collective_booking(booking, reason=reason, force=False)
    except educational_exceptions.CollectiveBookingAlreadyCancelled:
        raise ForbiddenError({"booking": "Impossible d'annuler une réservation déjà annulée"})
    except educational_exceptions.CollectiveBookingIsAlreadyUsed:
        raise ForbiddenError({"booking": "Cette réservation a déjà été utilisée et ne peut être annulée"})
    except educational_exceptions.BookingIsAlreadyRefunded:
        raise ForbiddenError(
            {"booking": "Cette réservation est en train d’être remboursée, il est impossible de l’invalider"}
        )

    educational_api_booking.notify_redactor_that_booking_has_been_cancelled(booking)
    educational_api_booking.notify_pro_that_booking_has_been_cancelled(booking)


def _get_booking(booking_id: int) -> models.CollectiveBooking | None:
    return (
        models.CollectiveBooking.query.filter(models.CollectiveBooking.id == booking_id)
        .join(models.CollectiveStock)
        .join(models.CollectiveOffer)
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .options(
            sa.orm.joinedload(models.CollectiveBooking.collectiveStock)
            .load_only(models.CollectiveStock.id)
            .joinedload(models.CollectiveStock.collectiveOffer)
            .load_only(models.CollectiveOffer.id),
        )
        .one_or_none()
    )
