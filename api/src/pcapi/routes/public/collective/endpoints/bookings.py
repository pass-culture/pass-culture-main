from werkzeug.exceptions import NotFound

from pcapi.core.educational import models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.models as providers_models
from pcapi.routes.public import blueprints
from pcapi.routes.public.collective.serialization import bookings as serialization
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


@blueprints.v2_prefixed_public_api.route("/collective/bookings/<int:booking_id>", methods=["GET"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        HTTP_200=(
            serialization.CollectiveBookingResponseModel,
            "Les informations d'une réservation collective",
        ),
        HTTP_401=(
            offers_serialization.AuthErrorResponseModel,
            "Authentification nécessaire",
        ),
    ),
)
@api_key_required
def get_collective_booking(booking_id: int) -> serialization.CollectiveBookingResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération les informations d'une réservation collective"""
    booking = (
        models.CollectiveBooking.query.filter(models.CollectiveBooking.id == booking_id)
        .join(models.CollectiveStock)
        .join(models.CollectiveOffer)
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .one_or_none()
    )
    if not booking:
        raise NotFound()

    return serialization.CollectiveBookingResponseModel.from_orm(booking)
