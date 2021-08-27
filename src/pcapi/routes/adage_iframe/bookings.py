import logging

from pcapi.connectors.api_adage import AdageException
from pcapi.connectors.api_adage import InstitutionalProjectRedactorNotFoundException
from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.educational_booking import BookEducationalOfferRequest
from pcapi.routes.adage_iframe.serialization.educational_booking import BookEducationalOfferResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/bookings", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=BookEducationalOfferResponse, on_error_statuses=[400])
@adage_jwt_required
def book_educational_offer(
    authenticated_information: AuthenticatedInformation, body: BookEducationalOfferRequest
) -> BookEducationalOfferResponse:
    if body.redactorEmail != authenticated_information.email:
        logger.info(
            "Authenticated email and redactor email do not match",
            extra={"email_token": authenticated_information.email, "email_body": (body.redactorEmail)},
        )
        raise ForbiddenError({"Authorization": "Authenticated email and redactor email do not match"})

    try:
        booking = educational_api.book_educational_offer(
            redactor_email=body.redactorEmail, uai_code=body.UAICode, stock_id=body.stockId
        )
    except AdageException as exception:
        logger.info(
            "Could not book offer: adage api call failed",
            extra={
                "redactor_email": body.redactorEmail,
                "status_code": str(exception.status_code),
                "response_text": exception.response_text,
            },
        )
        raise ApiErrors(
            {"global": "La récupération des informations du rédacteur de projet via Adage a échoué"},
            status_code=500,
        )
    except InstitutionalProjectRedactorNotFoundException:
        logger.info(
            "Could not book offer: redactor does not exist in Adage",
            extra={
                "redactor_email": body.redactorEmail,
            },
        )
        raise ApiErrors({"global": "Le rédacteur de projet n'existe pas dans Adage"}, status_code=404)
    except offers_exceptions.StockDoesNotExist:
        logger.info("Could not book offer: stock does not exist", extra={"stock_id": body.stockId})
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)
    except exceptions.StockNotBookable:
        logger.info("Could not book offer: stock is not bookable", extra={"stock_id": body.stockId})
        raise ApiErrors({"stock": "Cette offre n'est pas disponible à la réservation"})
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


@blueprint.adage_iframe.route("/authenticate", methods=["GET"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@adage_jwt_required
def authenticate(authenticated_information: AuthenticatedInformation) -> None:
    pass
