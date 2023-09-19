import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.public.united import utils
from pcapi.validation.routes.users_authentifications import current_api_key


COLLECTIVE_BOOKINGS_TAG = "Collective bookings"


@utils.public_api_route("/collective/bookings/<int:booking_id>", method="PATCH", tags=[COLLECTIVE_BOOKINGS_TAG])
def cancel_collective_booking(booking_id: int) -> None:
    """Cancel a collective booking"""
    booking = _get_booking(booking_id)
    if not booking:
        raise NotFound()

    try:
        reason = models.CollectiveBookingCancellationReasons.PUBLIC_API
        educational_api_booking.cancel_collective_booking(booking, reason=reason)
    except educational_exceptions.CollectiveBookingAlreadyCancelled:
        raise ApiErrors({"booking": "Already cancelled"}, status_code=403)
    except educational_exceptions.BookingIsAlreadyRefunded:
        raise ApiErrors({"booking": "Already reimbursed: can't cancel"}, status_code=403)

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
