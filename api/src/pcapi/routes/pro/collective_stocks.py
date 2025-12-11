import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import exceptions
from pcapi.core.educational import repository
from pcapi.core.educational.api import stock as educational_api_stock
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.routes.apis import private_api
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import collective_stock_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@private_api.route("/collective/stocks", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=201,
    on_error_statuses=[400, 404],
    response_model=collective_stock_serialize.CollectiveStockResponseModel,
    api=blueprint.pro_private_schema,
)
def create_collective_stock(
    body: collective_stock_serialize.CollectiveStockCreationBodyModel,
) -> collective_stock_serialize.CollectiveStockResponseModel:
    try:
        offerer = offerers_repository.get_by_collective_offer_id(body.offerId)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ResourceNotFoundError({"offerer": ["Aucune structure trouvée à partir de cette offre"]})
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        collective_stock = educational_api_stock.create_collective_stock(body)
    except exceptions.CollectiveStockAlreadyExists:
        raise ApiErrors({"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"})
    except exceptions.StartAndEndEducationalYearDifferent:
        raise ApiErrors({"code": "START_AND_END_EDUCATIONAL_YEAR_DIFFERENT"})
    except exceptions.StartEducationalYearMissing:
        raise ApiErrors({"code": "START_EDUCATIONAL_YEAR_MISSING"})
    except exceptions.EndEducationalYearMissing:
        raise ApiErrors({"code": "END_EDUCATIONAL_YEAR_MISSING"})
    except exceptions.EducationalException as exc:
        raise ApiErrors(exc.errors)

    return collective_stock_serialize.CollectiveStockResponseModel.model_validate(collective_stock)


@private_api.route("/collective/stocks/<int:collective_stock_id>", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[400, 401, 404],
    api=blueprint.pro_private_schema,
    response_model=collective_stock_serialize.CollectiveStockResponseModel,
)
def edit_collective_stock(
    collective_stock_id: int, body: collective_stock_serialize.CollectiveStockEditionBodyModel
) -> collective_stock_serialize.CollectiveStockResponseModel:
    collective_stock = repository.get_collective_stock(collective_stock_id)
    if collective_stock is None:
        raise ResourceNotFoundError({"code": "COLLECTIVE_STOCK_NOT_FOUND"})

    try:
        offerer = offerers_repository.get_by_collective_stock_id(collective_stock.id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ResourceNotFoundError({"offerer": ["Aucune structure trouvée à partir de cette offre"]})
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        educational_api_stock.edit_collective_stock(
            stock=collective_stock, stock_data=body.model_dump(exclude_unset=True)
        )
        return collective_stock_serialize.CollectiveStockResponseModel.model_validate(collective_stock)
    except exceptions.CollectiveOfferIsPublicApi:
        raise ForbiddenError({"global": ["Les stocks créés par l'api publique ne sont pas editables."]})
    except exceptions.CollectiveOfferForbiddenAction:
        raise ForbiddenError({"global": ["Cette action n'est pas autorisée sur l'offre collective liée à ce stock."]})
    except exceptions.EndDatetimeBeforeStartDatetime:
        raise ApiErrors({"educationalStock": ["La date de fin de l'évènement ne peut précéder la date de début."]})
    except (
        offers_exceptions.BookingLimitDatetimeTooLate
    ):  # (tcoudray-pass, 14/05/2025) TODO: Refactor, educational_api should not raise this kind of error
        raise ApiErrors(
            {"educationalStock": ["La date limite de confirmation ne peut être fixée après la date de l évènement"]}
        )
    except (
        offers_exceptions.OfferException,
    ) as error:  # (tcoudray-pass, 14/05/2025) TODO: Refactor, should not raise this kind of error
        raise ApiErrors(error.errors)
    except exceptions.StartAndEndEducationalYearDifferent:
        raise ApiErrors({"code": "START_AND_END_EDUCATIONAL_YEAR_DIFFERENT"})
    except exceptions.StartEducationalYearMissing:
        raise ApiErrors({"code": "START_EDUCATIONAL_YEAR_MISSING"})
    except exceptions.EndEducationalYearMissing:
        raise ApiErrors({"code": "END_EDUCATIONAL_YEAR_MISSING"})
