import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational.repository import get_collective_stock_for_offer
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.offerers.api as offerers_api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockCreationBodyModel
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockIdResponseModel
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize_or_raise
from pcapi.utils.rest import check_user_has_access_to_offerer


logger = logging.getLogger(__name__)


@private_api.route("/collective/offers/<offer_id>/stock", methods=["GET"])
@login_required
@spectree_serialize(response_model=CollectiveStockResponseModel, api=blueprint.pro_private_schema)
def get_collective_stock(offer_id: str) -> CollectiveStockResponseModel:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(dehumanize_or_raise(offer_id))
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offerer.id)
    stock = get_collective_stock_for_offer(dehumanize_or_raise(offer_id))

    if stock is None:
        raise ApiErrors({"stock": ["Aucun stock trouvé à partir de cette offre"]}, status_code=404)

    return CollectiveStockResponseModel.from_orm(stock)


@private_api.route("/collective/stocks", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201, response_model=CollectiveStockIdResponseModel, api=blueprint.pro_private_schema
)
def create_collective_stock(body: CollectiveStockCreationBodyModel) -> CollectiveStockIdResponseModel:
    try:
        offerer = offerers_repository.get_by_collective_offer_id(body.offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        collective_stock = educational_api.create_collective_stock(body, current_user)
    except educational_exceptions.CollectiveStockAlreadyExists:
        raise ApiErrors({"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"}, status_code=409)

    return CollectiveStockIdResponseModel.from_orm(collective_stock)
