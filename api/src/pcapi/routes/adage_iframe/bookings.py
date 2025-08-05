import logging

from pcapi.core.educational import exceptions
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.educational.models import AdageFrontRoles
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.routes.adage_iframe.serialization.collective_bookings import BookCollectiveOfferRequest
from pcapi.routes.adage_iframe.serialization.collective_bookings import BookCollectiveOfferResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/collective/bookings", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, response_model=BookCollectiveOfferResponse, on_error_statuses=[400, 403])
@adage_jwt_required
def book_collective_offer(
    body: BookCollectiveOfferRequest, authenticated_information: AuthenticatedInformation
) -> BookCollectiveOfferResponse:
    if not authenticated_information.canPrebook:
        raise ApiErrors({"global": "Could not book offer: not allowed"}, status_code=403)

    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="BookingConfirmationButtonClick",
        extra_data={"stockId": body.stockId},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    try:
        booking = educational_api_booking.book_collective_offer(
            redactor_informations=get_redactor_information_from_adage_authentication(authenticated_information),
            stock_id=body.stockId,
        )
    except exceptions.AdageException as exception:
        logger.info(
            "Could not book offer: adage api call failed",
            extra={
                "redactor_email": authenticated_information.email,
                "status_code": str(exception.status_code),
                "response_text": exception.response_text,
            },
        )
        raise ApiErrors(
            {"global": "La récupération des informations du rédacteur de projet via Adage a échoué"},
            status_code=500,
        )

    except exceptions.MissingRequiredRedactorInformation:
        logger.info(
            "Could not book offer: missing information in adage jwt",
            extra={"authenticated_information": authenticated_information.dict()},
        )
        raise ApiErrors(
            {
                "authorization": "Des informations sur le rédacteur de projet, et nécessaires à la préréservation, sont manquantes"
            },
            status_code=403,
        )

    except exceptions.CollectiveStockDoesNotExist:
        logger.info("Could not book offer: stock does not exist", extra={"stock_id": body.stockId})
        raise ApiErrors({"stock": "Stock introuvable"}, status_code=400)
    except exceptions.CollectiveStockNotBookableByUser:
        logger.info(
            "Could not book offer: uai code does not match",
            extra={"stock_id": body.stockId, "uai": authenticated_information.uai},
        )
        raise ApiErrors({"code": "WRONG_UAI_CODE"}, status_code=403)

    except exceptions.CollectiveStockNotBookable:
        logger.info("Could not book offer: stock is not bookable", extra={"stock_id": body.stockId})
        raise ApiErrors({"stock": "Cette offre n'est pas disponible à la réservation"})
    except exceptions.EducationalInstitutionUnknown:
        logger.info(
            "Could not book offer: educational institution not found", extra={"uai_code": authenticated_information.uai}
        )
        raise ApiErrors({"code": "UNKNOWN_EDUCATIONAL_INSTITUTION"})
    except exceptions.EducationalYearNotFound:
        logger.info("Could not book offer: associated educational year not found", extra={"stock_id": body.stockId})
        raise ApiErrors({"educationalYear": "Aucune année scolaire ne correspond à cet évènement"})

    return BookCollectiveOfferResponse(bookingId=booking.id)
