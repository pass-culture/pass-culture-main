import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational.repository import get_collective_stock_for_offer
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.offerers.api as offerers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import collective_stock_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize_or_raise
from pcapi.utils.rest import check_user_has_access_to_offerer


logger = logging.getLogger(__name__)


@private_api.route("/collective/offers/<offer_id>/stock", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=collective_stock_serialize.CollectiveStockResponseModel, api=blueprint.pro_private_schema
)
def get_collective_stock(offer_id: str) -> collective_stock_serialize.CollectiveStockResponseModel:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(dehumanize_or_raise(offer_id))
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offerer.id)  # type: ignore [arg-type]
    stock = get_collective_stock_for_offer(dehumanize_or_raise(offer_id))

    if stock is None:
        raise ApiErrors({"stock": ["Aucun stock trouvé à partir de cette offre"]}, status_code=404)

    return collective_stock_serialize.CollectiveStockResponseModel.from_orm(stock)


@private_api.route("/collective/stocks", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=collective_stock_serialize.CollectiveStockIdResponseModel,
    api=blueprint.pro_private_schema,
)
def create_collective_stock(
    body: collective_stock_serialize.CollectiveStockCreationBodyModel,
) -> collective_stock_serialize.CollectiveStockIdResponseModel:
    try:
        offerer = offerers_repository.get_by_collective_offer_id(body.offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)  # type: ignore [arg-type]

    try:
        collective_stock = educational_api.create_collective_stock(body, current_user)
    except educational_exceptions.CollectiveStockAlreadyExists:
        raise ApiErrors({"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"}, status_code=409)

    return collective_stock_serialize.CollectiveStockIdResponseModel.from_orm(collective_stock)


@private_api.route("/collective/stocks/<collective_stock_id>", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[400, 401, 404, 422],
    api=blueprint.pro_private_schema,
    response_model=collective_stock_serialize.CollectiveStockResponseModel,
)
def edit_collective_stock(
    collective_stock_id: str, body: collective_stock_serialize.CollectiveStockEditionBodyModel
) -> collective_stock_serialize.CollectiveStockResponseModel:
    collective_stock = educational_api.get_collective_stock(dehumanize_or_raise(collective_stock_id))
    if collective_stock is None:
        raise ApiErrors({"code": "COLLECTIVE_STOCK_NOT_FOUND"}, status_code=404)

    try:
        offerer = offerers_repository.get_by_collective_stock_id(collective_stock.id)  # type: ignore [arg-type]
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)  # type: ignore [arg-type]

    try:
        collective_stock = educational_api.edit_collective_stock(
            collective_stock,
            body.dict(exclude_unset=True),
        )
        return collective_stock_serialize.CollectiveStockResponseModel.from_orm(collective_stock)
    except offers_exceptions.BookingLimitDatetimeTooLate:
        raise ApiErrors(
            {"educationalStock": ["La date limite de confirmation ne peut être fixée après la date de l évènement"]},
            status_code=400,
        )
    except offers_exceptions.EducationalOfferStockBookedAndBookingNotPending as error:
        raise ApiErrors(
            {
                "educationalStockEdition": [
                    f"Un stock lié à une offre éducationnelle, dont la réservation associée a le statut {error.booking_status.value}, ne peut être édité "
                ]
            },
            status_code=400,
        )
