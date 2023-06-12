from pcapi.core.bookings import exceptions
from pcapi.core.bookings import models as booking_models
from pcapi.core.bookings import validation as bookings_validation
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import api_errors
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key

from . import blueprint
from . import bookings_serialization as serialization


def _get_booking_by_token(token: str) -> booking_models.Booking:
    return (
        booking_models.Booking.query.filter_by(token=token.upper())
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .join(offers_models.Stock)
        .join(offers_models.Offer)
        .one_or_none()
    )


@blueprint.v1_bookings_blueprint.route("/token/<string:token>", methods=["GET"])
@spectree_serialize(api=blueprint.v1_bookings_schema, response_model=serialization.GetBookingResponse)
@api_key_required
def get_booking_by_token(token: str) -> serialization.GetBookingResponse:
    booking = _get_booking_by_token(token)
    if booking is None:
        raise api_errors.ApiErrors(errors={"global": "This countermark cannot be found"}, status_code=404)

    try:
        bookings_validation.check_is_usable(booking)
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ApiErrors(errors={"payment": "This booking has already been reimbursed"}, status_code=403)
    except exceptions.BookingIsAlreadyUsed:
        raise api_errors.ApiErrors(errors={"booking": "This booking has already been validated"}, status_code=410)
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ApiErrors(errors={"booking": "This booking has been canceled"}, status_code=410)
    except exceptions.BookingIsNotConfirmed as exc:
        raise api_errors.ApiErrors(errors={"booking": str(exc)}, status_code=403)

    return serialization.GetBookingResponse.build_booking(booking)
