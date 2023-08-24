import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models
from pcapi.core.educational.api import booking as educational_api_booking
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.models as providers_models
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.public import blueprints
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


@blueprints.v2_prefixed_public_api.route("/collective/bookings/<int:booking_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives"],
    on_success_status=204,
    resp=SpectreeResponse(
        HTTP_204=(None, "Annuler une réservation collective"),
        HTTP_401=(
            offers_serialization.AuthErrorResponseModel,
            "Authentification nécessaire",
        ),
    ),
)
@api_key_required
def cancel_collective_booking(booking_id: int) -> None:
    # in French, to be used by Swagger for the API documentation
    """Annuler une réservation collective"""
    booking = _get_booking(booking_id)
    if not booking:
        raise NotFound()

    try:
        reason = models.CollectiveBookingCancellationReasons.PUBLIC_API
        educational_api_booking.cancel_collective_booking(booking, reason=reason)
    except educational_exceptions.CollectiveBookingAlreadyCancelled:
        raise ApiErrors({"booking": "Impossible d'annuler une réservation déjà annulée"}, status_code=403)
    except educational_exceptions.BookingIsAlreadyRefunded:
        raise ApiErrors({"booking": "Impossible d'annuler une réservation remboursée"}, status_code=403)


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
