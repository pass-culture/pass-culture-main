import logging

from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.matomo import matomo
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.collective_bookings import BookCollectiveOfferRequest
from pcapi.routes.adage_iframe.serialization.collective_bookings import BookCollectiveOfferResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/collective/bookings", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=BookCollectiveOfferResponse, on_error_statuses=[400, 403])
@adage_jwt_required
@matomo()
def book_collective_offer(
    body: BookCollectiveOfferRequest,
    authenticated_information: AuthenticatedInformation,
) -> BookCollectiveOfferResponse:
    try:
        booking = educational_api.book_collective_offer(
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

    except offers_exceptions.StockDoesNotExist:
        logger.info("Could not book offer: stock does not exist", extra={"stock_id": body.stockId})
        raise ApiErrors({"stock": "Stock introuvable"}, status_code=400)
    except exceptions.CollectiveStockNotBookableByUser:
        logger.info(
            "Could not book offer: uai code does not match",
            extra={"stock_id": body.stockId, "uai": authenticated_information.uai},
        )
        raise ApiErrors({"code": "WRONG_UAI_CODE"}, status_code=403)

    except exceptions.StockNotBookable:
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
