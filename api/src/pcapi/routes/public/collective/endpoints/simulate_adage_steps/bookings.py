from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.educational import exceptions
from pcapi.core.educational.api import booking as booking_api
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.routes.adage.v1.serialization import constants
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.endpoints.simulate_adage_steps import utils
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprints.public_api.route("/v2/collective/adage_mock/bookings/<int:booking_id>/confirm", methods=["POST"])
@utils.exclude_prod_environment
@api_key_required
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
    except exceptions.EducationalBookingNotFound:
        raise ResourceNotFoundError({"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND})
    except exceptions.EducationalDepositNotFound:
        raise ResourceNotFoundError({"code": "DEPOSIT_NOT_FOUND"})
