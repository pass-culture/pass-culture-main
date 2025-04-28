from contextlib import suppress
from datetime import datetime
import logging

import sqlalchemy.orm as sa_orm

from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational.api import booking as booking_api
from pcapi.core.educational.schemas import RedactorInformation
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.repository.session_management import atomic
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.endpoints.adage_mock import utils
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required


logger = logging.getLogger(__name__)


class BookedCollectiveOffer(ConfiguredBaseModel):
    booking_id: int
    booking_status: models.CollectiveBookingStatus


@blueprints.public_api.route("/v2/collective/adage_mock/bookings/<int:booking_id>/confirm", methods=["POST"])
@atomic()
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

    **WARNING:** this endpoint is not available from the production
    environment as it is a mock meant to ease the test of your
    integrations.
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
@atomic()
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

    **WARNING:** this endpoint is not available from the production
    environment as it is a mock meant to ease the test of your
    integrations.
    """
    booking = _get_booking_or_raise_404(booking_id)

    try:
        reason = models.CollectiveBookingCancellationReasons.PUBLIC_API
        booking_api.cancel_collective_booking(booking, reason=reason, _from="adage_mock_api")
    except exceptions.CollectiveBookingAlreadyCancelled:
        raise ForbiddenError({"code": "ALREADY_CANCELLED_BOOKING"})
    except exceptions.BookingIsAlreadyRefunded:
        raise ForbiddenError({"code": "BOOKING_IS_REIMBURSED"})
    except Exception:
        err_extras = {"booking": booking.id, "api_key_id": current_api_key.id}
        logger.exception("Adage mock. Failed to cancel booking.", extra=err_extras)
        raise ApiErrors({"code": "FAILED_TO_CANCEL_BOOKING_TRY_AGAIN"}, status_code=500)


@blueprints.public_api.route("/v2/collective/bookings/<int:booking_id>/use", methods=["POST"])
@atomic()
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
        booking.dateUsed = datetime.utcnow()
        booking.status = models.CollectiveBookingStatus.USED

        finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED,
            booking=booking,
        )
    except Exception:
        err_extras = {"booking": booking.id, "api_key_id": current_api_key.id}
        logger.exception("[adage mock] failed to use booking", extra=err_extras)
        raise ApiErrors({"code": "FAILED_TO_USE_BOOKING_TRY_AGAIN_LATER"}, status_code=500)


@blueprints.public_api.route("/v2/collective/adage_mock/bookings/<int:booking_id>/pending", methods=["POST"])
@atomic()
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

    **WARNING:** this endpoint is not available from the production
    environment as it is a mock meant to ease the test of your
    integrations.
    """
    booking = _get_booking_or_raise_404(booking_id)

    if booking.status == models.CollectiveBookingStatus.USED:
        raise ForbiddenError({"code": "CANNOT_SET_BACK_USED_BOOKING_TO_PENDING"})
    if booking.status == models.CollectiveBookingStatus.REIMBURSED:
        raise ForbiddenError({"code": "CANNOT_SET_BACK_REIMBURSED_BOOKING_TO_PENDING"})

    try:
        if booking.status == models.CollectiveBookingStatus.CANCELLED:
            booking.uncancel_booking()
            db.session.flush()
    except Exception:
        err_extras = {"booking": booking.id, "api_key_id": current_api_key.id}
        logger.exception("Adage mock. Failed to set cancelled booking back to pending state", extra=err_extras)
        raise ApiErrors({"code": "FAILED_TO_SET_BACK_CANCELLED_BOOKING_TO_PENDING"}, status_code=500)

    try:
        booking.status = models.CollectiveBookingStatus.PENDING
        booking.confirmationDate = None

        db.session.add(booking)
        db.session.flush()
    except Exception:
        err_extras = {"booking": booking.id, "api_key_id": current_api_key.id}
        logger.exception("Adage mock. Failed to set booking back to pending state", extra=err_extras)
        raise ApiErrors({"code": "FAILED_TO_SET_BACK_BOOKING_TO_PENDING"}, status_code=500)


@blueprints.public_api.route("/v2/collective/adage_mock/bookings/<int:booking_id>/reimburse", methods=["POST"])
@atomic()
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
def reimburse_collective_booking(booking_id: int) -> None:
    """
    Mock collective booking reimbursement.

    Like this could happen within the Adage platform.

    **WARNING:** this endpoint is not available from the production
    environment as it is a mock meant to ease the test of your
    integrations.
    """
    booking = _get_booking_or_raise_404(booking_id)

    if booking.status != models.CollectiveBookingStatus.USED:
        raise ForbiddenError({"code": f"CANNOT_REIMBURSE_{booking.status.value}_BOOKING"})

    try:
        booking.status = models.CollectiveBookingStatus.REIMBURSED
        booking.reimbursementDate = datetime.utcnow()

        db.session.add(booking)
        db.session.flush()
    except Exception:
        err_extras = {"booking": booking.id, "api_key_id": current_api_key.id}
        logger.exception("Adage mock. Failed to repay booking.", extra=err_extras)

        raise ApiErrors({"code": "REPAYMENT_FAILED_TRY_AGAIN_LATER"}, status_code=500)


@blueprints.public_api.route("/v2/collective/adage_mock/offer/<int:offer_id>/book", methods=["POST"])
@atomic()
@utils.exclude_prod_environment
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    on_success_status=200,
    response_model=BookedCollectiveOffer,
    tags=[tags.COLLECTIVE_ADAGE_MOCK],
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_200_REQUEST_SUCCESSFUL
            | http_responses.HTTP_403_UNAUTHORIZED
            | http_responses.HTTP_404_COLLECTIVE_OFFER_NOT_FOUND
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def adage_mock_book_offer(offer_id: int) -> BookedCollectiveOffer:
    """
    Mock collective offer booking

    Like this could happen within the Adage platform.

    **WARNING:** this endpoint is not available from the production
    environment as it is a mock meant to ease the test of your
    integrations.
    """
    offer = _get_offer_or_raise_404(offer_id)

    if not offer.isBookable:
        with suppress(AttributeError):
            if offer.collectiveStock.collectiveBookings:
                raise ForbiddenError({"code": "OFFER_IS_NOT_BOOKABLE_BECAUSE_BOOKING_EXISTS"})
        raise ForbiddenError({"code": "OFFER_IS_NOT_BOOKABLE"})

    institution = offer.institution
    if not institution:
        raise ForbiddenError({"code": "OFFER_IS_NOT_LINKED_TO_AN_INSTITUTION"})

    uai = institution.institutionId
    redactor_information = RedactorInformation(
        civility="", lastname=f"integration {uai}", firstname="redactor", email=f"redactor.{uai}@example.fr", uai=uai
    )

    try:
        booking = booking_api.book_collective_offer(redactor_information, offer.collectiveStock.id)
    except exceptions.EducationalYearNotFound:
        raise ForbiddenError({"code": "OFFERS_YEAR_NOT_FOUND"})
    except Exception:
        err_extras = {"offer": offer_id, "api_key_id": current_api_key.id}
        logger.exception("Adage mock. Failed to prebook offer.", extra=err_extras)

        raise ApiErrors({"code": "OFFER_BOOKING_FAILED_TRY_AGAIN_LATER"}, status_code=500)

    return BookedCollectiveOffer(booking_id=booking.id, booking_status=booking.status)


def _get_offer_or_raise_404(offer_id: int) -> models.CollectiveOffer:
    offer = (
        db.session.query(models.CollectiveOffer)
        .filter(models.CollectiveOffer.id == offer_id)
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .options(sa_orm.joinedload(models.CollectiveOffer.institution))
        .options(
            sa_orm.selectinload(models.CollectiveOffer.collectiveStock).joinedload(
                models.CollectiveStock.collectiveBookings
            )
        )
        .options(sa_orm.selectinload(models.CollectiveOffer.venue).joinedload(offerers_models.Venue.managingOfferer))
        .one_or_none()
    )

    if not offer:
        raise ResourceNotFoundError({"code": "OFFER_NOT_FOUND"})
    return offer


def _get_booking_or_raise_404(booking_id: int) -> models.CollectiveBooking:
    booking = (
        db.session.query(models.CollectiveBooking)
        .filter(models.CollectiveBooking.id == booking_id)
        .join(models.CollectiveStock)
        .join(models.CollectiveOffer)
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .options(
            sa_orm.joinedload(models.CollectiveBooking.collectiveStock)
            .load_only(
                models.CollectiveStock.id, models.CollectiveStock.startDatetime, models.CollectiveStock.endDatetime
            )
            .joinedload(models.CollectiveStock.collectiveOffer)
            .load_only(models.CollectiveOffer.id),
        )
        .one_or_none()
    )

    if not booking:
        raise ResourceNotFoundError({"code": "BOOKING_NOT_FOUND"})
    return booking
