import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational.api import stock as educational_api_stock
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import collective_stock_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer


logger = logging.getLogger(__name__)


@private_api.route("/collective/stocks", methods=["POST"])
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
        offerer = offerers_repository.get_by_collective_offer_id(body.offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        collective_stock = educational_api_stock.create_collective_stock(body, current_user)
    except educational_exceptions.CollectiveStockAlreadyExists:
        raise ApiErrors({"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"}, status_code=400)
    except educational_exceptions.StartAndEndEducationalYearDifferent:
        raise ApiErrors({"code": "START_AND_END_EDUCATIONAL_YEAR_DIFFERENT"}, status_code=400)

    return collective_stock_serialize.CollectiveStockResponseModel.from_orm(collective_stock)


@private_api.route("/collective/stocks/<int:collective_stock_id>", methods=["PATCH"])
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
    collective_stock = educational_api_stock.get_collective_stock(collective_stock_id)
    if collective_stock is None:
        raise ApiErrors({"code": "COLLECTIVE_STOCK_NOT_FOUND"}, status_code=404)

    try:
        offerer = offerers_repository.get_by_collective_stock_id(collective_stock.id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        collective_stock = educational_api_stock.edit_collective_stock(
            collective_stock,
            body.dict(exclude_unset=True),
        )
        return collective_stock_serialize.CollectiveStockResponseModel.from_orm(collective_stock)
    except educational_exceptions.CollectiveOfferIsPublicApi:
        raise ApiErrors({"global": ["Les stocks créés par l'api publique ne sont pas editables."]}, 403)
    except offers_exceptions.BookingLimitDatetimeTooLate:
        raise ApiErrors(
            {"educationalStock": ["La date limite de confirmation ne peut être fixée après la date de l évènement"]},
            status_code=400,
        )
    except educational_exceptions.PriceRequesteCantBedHigherThanActualPrice:
        raise ApiErrors(
            {"educationalStock": "Le prix demandé ne peux être supérieur aux prix actuel si l'offre a été confirmée."},
            status_code=403,
        )
    except offers_exceptions.OfferEditionBaseException as error:
        raise ApiErrors(error.errors, status_code=400)
    except educational_exceptions.StartAndEndEducationalYearDifferent:
        raise ApiErrors({"code": "START_AND_END_EDUCATIONAL_YEAR_DIFFERENT"}, status_code=400)
