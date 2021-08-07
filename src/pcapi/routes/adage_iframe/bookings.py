import logging

from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.educational_booking import BookEducationalOfferRequest
from pcapi.routes.adage_iframe.serialization.educational_booking import BookEducationalOfferResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/bookings", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=BookEducationalOfferResponse, on_error_statuses=[400])
@adage_jwt_required
def book_educational_offer(authenticated_email: str, body: BookEducationalOfferRequest) -> BookEducationalOfferResponse:
    if body.redactorEmail != authenticated_email:
        logger.info(
            "Authenticated email and redactor email do not match",
            extra={"email_token": authenticated_email, "email_body": (body.redactorEmail)},
        )
        raise ForbiddenError({"Authorization": "Authenticated email and redactor email do not match"})

    try:
        booking = educational_api.book_educational_offer(
            redactor_email=(body.redactorEmail), uai_code=body.UAICode, stock_id=body.stockId
        )
    except offers_exceptions.StockDoesNotExist:
        logger.info("Could not book offer: stock does not exist", extra={"stock_id": body.stockId})
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)
    except exceptions.NoStockLeftError:
        logger.info("Could not book offer: no stock left", extra={"stock_id": body.stockId})
        raise ApiErrors({"stock": "Il n'y a plus de stock disponible à la réservation sur cette offre"})
    except exceptions.OfferIsNotEvent:
        logger.info("Could not book offer: offer is not an event", extra={"stock_id": body.stockId})
        raise ApiErrors({"offer": "L'offre n'est pas un évènement"})
    except exceptions.OfferIsNotEducational:
        logger.info("Could not book offer: offer is not educational", extra={"stock_id": body.stockId})
        raise ApiErrors({"offer": "L'offre n'est pas une offre éducationnelle"})
    except exceptions.EducationalInstitutionUnknown:
        logger.info("Could not book offer: educational institution not found", extra={"uai_code": body.UAICode})
        raise ApiErrors({"educationalInstitution": "L'établissement n'existe pas"})
    except exceptions.EducationalYearNotFound:
        logger.info("Could not book offer: associated educational year not found", extra={"stock_id": body.stockId})
        raise ApiErrors({"educationalYear": "Aucune année scolaire ne correspond à cet évènement"})

    return BookEducationalOfferResponse(bookingId=booking.id)
