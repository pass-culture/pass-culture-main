from datetime import datetime
from datetime import timezone
import logging

import sqlalchemy as sa

from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational.api import booking as booking_api
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.repository import atomic
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.endpoints.adage_mock import utils
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required


logger = logging.getLogger(__name__)


@blueprints.public_api.route("/v2/collective/adage_mock/bookings/<int:booking_id>/confirm", methods=["POST"])
@utils.exclude_prod_environment
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    on_success_status=204,
    tags=[tags.COLLECTIVE_ADAGE_MOCK],
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_COLLECTIVE_BOOKING_STATUS_UPDATE
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_403_COLLECTIVE_BOOKING_STATUS_UPDATE_REFUSED
            | http_responses.HTTP_404_COLLECTIVE_OFFER_NOT_FOUND
        )
    ),
)
def confirm_collective_booking(booking_id: int) -> None:
    """
    Mock collective booking confirmation

    Like this could happen within the Adage platform.

    Warning: not available for production nor integration environments
    """
    _get_booking_or_raise_404(booking_id)  # check booking is linked to the provider
    try:
        booking_api.confirm_collective_booking(booking_id)
    except exceptions.InsufficientFund:
        raise ForbiddenError({"code": "INSUFFICIENT_FUND"})
    except exceptions.InsufficientMinistryFund:
        raise ForbiddenError({"code": "INSUFFICIENT_MINISTRY_FUND"})
    except exceptions.InsufficientTemporaryFund:
        raise ForbiddenError({"code": "INSUFFICIENT_FUND_DEPOSIT_NOT_FINAL"})
    except exceptions.BookingIsCancelled:
        raise ForbiddenError({"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"})
    except bookings_exceptions.ConfirmationLimitDateHasPassed:
        raise ForbiddenError({"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"})
    except exceptions.EducationalDepositNotFound:
        raise ResourceNotFoundError({"code": "DEPOSIT_NOT_FOUND"})


@blueprints.public_api.route("/v2/collective/adage_mock/bookings/<int:booking_id>/cancel", methods=["POST"])
@utils.exclude_prod_environment
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    on_success_status=204,
    tags=[tags.COLLECTIVE_ADAGE_MOCK],
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_COLLECTIVE_BOOKING_STATUS_UPDATE
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_403_COLLECTIVE_BOOKING_STATUS_UPDATE_REFUSED
            | http_responses.HTTP_404_COLLECTIVE_OFFER_NOT_FOUND
        )
    ),
)
def adage_mock_cancel_collective_booking(booking_id: int) -> None:
    """
    Mock collective booking cancellation

    Like this could happen within the Adage platform.

    Warning: not available for production nor integration environments
    """
    booking = _get_booking_or_raise_404(booking_id)

    try:
        reason = models.CollectiveBookingCancellationReasons.PUBLIC_API
        booking_api.cancel_collective_booking(booking, reason=reason, _from="adage_mock_api")
    except exceptions.CollectiveBookingAlreadyCancelled:
        raise ForbiddenError({"code": "ALREADY_CANCELLED_BOOKING"})
    except exceptions.BookingIsAlreadyRefunded:
        raise ForbiddenError({"code": "BOOKING_IS_REIMBURSED"})
    except Exception as err:
        err_extras = {"booking": booking_id, "api_key": current_api_key.id, "err": str(err)}
        logger.error("Adage mock. Failed to cancel booking.", extra=err_extras)
        raise ApiErrors({"code": "FAILED_TO_CANCEL_BOOKING_TRY_AGAIN"}, status_code=500)


@blueprints.public_api.route("/v2/collective/bookings/<int:booking_id>/use", methods=["POST"])
@utils.exclude_prod_environment
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    on_success_status=204,
    tags=[tags.COLLECTIVE_ADAGE_MOCK],
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_COLLECTIVE_BOOKING_STATUS_UPDATE
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_403_COLLECTIVE_BOOKING_STATUS_UPDATE_REFUSED
            | http_responses.HTTP_404_COLLECTIVE_OFFER_NOT_FOUND
        )
    ),
)
def use_collective_booking(booking_id: int) -> None:
    """
    Mock collective booking use

    Mark collective booking as used to mock what would automatically
    happen 48h after the event.

    **WARNING:** this endpoint is not available from the production
    environment as it is a mock meant to ease the test of your
    integrations.
    """
    booking = _get_booking_or_raise_404(booking_id)

    if booking.status != models.CollectiveBookingStatus.CONFIRMED:
        raise ForbiddenError({"code": "ONLY_CONFIRMED_BOOKING_CAN_BE_USED"})

    try:
        with atomic():
            booking.dateUsed = datetime.now(timezone.utc)  # pylint: disable=datetime-now
            booking.status = models.CollectiveBookingStatus.USED

            finance_api.add_event(
                finance_models.FinanceEventMotive.BOOKING_USED,
                booking=booking,
            )
    except Exception as err:
        logger.error("[adage mock] failed to use booking", extra={"booking": booking.id, "error": str(err)})
        raise ApiErrors({"code": "FAILED_TO_USE_BOOKING_TRY_AGAIN_LATER"}, status_code=500)


@blueprints.public_api.route("/v2/collective/adage_mock/bookings/<int:booking_id>/pending", methods=["POST"])
@utils.exclude_prod_environment
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    on_success_status=204,
    tags=[tags.COLLECTIVE_ADAGE_MOCK],
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_COLLECTIVE_BOOKING_STATUS_UPDATE
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_403_COLLECTIVE_BOOKING_STATUS_UPDATE_REFUSED
            | http_responses.HTTP_404_COLLECTIVE_OFFER_NOT_FOUND
        )
    ),
)
def reset_collective_booking(booking_id: int) -> None:
    """
    Adage mock: reset collective booking back to pending state.

    Like this could happen within the Adage platform.

    Warning: not available for production nor integration environments
    """
    booking = _get_booking_or_raise_404(booking_id)

    if booking.status == models.CollectiveBookingStatus.USED:
        raise ForbiddenError({"code": "CANNOT_SET_BACK_USED_BOOKING_TO_PENDING"})
    if booking.status == models.CollectiveBookingStatus.REIMBURSED:
        raise ForbiddenError({"code": "CANNOT_SET_BACK_REIMBURSED_BOOKING_TO_PENDING"})

    try:
        if booking.status == models.CollectiveBookingStatus.CANCELLED:
            booking.uncancel_booking()
    except Exception as err:
        db.session.rollback()

        err_extras = {"booking": booking.id, "api_key": current_api_key.id, "err": str(err)}
        logger.error("Adage mock. Failed to set cancelled booking back to pending state", extra=err_extras)
        raise ApiErrors({"code": "FAILED_TO_SET_BACK_CANCELLED_BOOKING_TO_PENDING"}, status_code=500)

    try:
        booking.status = models.CollectiveBookingStatus.PENDING
        booking.confirmationDate = None

        db.session.add(booking)
        db.session.commit()
    except Exception as err:
        db.session.rollback()

        err_extras = {"booking": booking.id, "api_key": current_api_key.id, "err": str(err)}
        logger.error("Adage mock. Failed to set booking back to pending state", extra=err_extras)
        raise ApiErrors({"code": "FAILED_TO_SET_BACK_BOOKING_TO_PENDING"}, status_code=500)


def _get_booking_or_raise_404(booking_id: int) -> models.CollectiveBooking:
    booking = (
        models.CollectiveBooking.query.filter(models.CollectiveBooking.id == booking_id)
        .join(models.CollectiveStock)
        .join(models.CollectiveOffer)
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .options(
            sa.orm.joinedload(models.CollectiveBooking.collectiveStock)
            .load_only(models.CollectiveStock.id, models.CollectiveStock.beginningDatetime)
            .joinedload(models.CollectiveStock.collectiveOffer)
            .load_only(models.CollectiveOffer.id),
        )
        .one_or_none()
    )

    if not booking:
        raise ResourceNotFoundError({"code": "BOOKING_NOT_FOUND"})
    return booking
