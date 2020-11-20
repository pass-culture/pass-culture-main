import pcapi.core.offers.api as offers_api
from pcapi.flask_app import private_api
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models import VenueSQLEntity
from pcapi.models.user_offerer import RightsType
from pcapi.repository import offerer_queries
from pcapi.repository.offer_queries import get_offer_by_id
from pcapi.routes.serialization.stock_serialize import StockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockEditionBodyModel
from pcapi.routes.serialization.stock_serialize import StockResponseIdModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import ensure_current_user_has_rights
from pcapi.utils.rest import login_or_api_key_required


@private_api.route("/stocks", methods=["POST"])
@login_or_api_key_required
@spectree_serialize(on_success_status=201, response_model=StockResponseIdModel)
def create_stock(body: StockCreationBodyModel) -> StockResponseIdModel:
    offerer = offerer_queries.get_by_offer_id(body.offer_id)
    ensure_current_user_has_rights(RightsType.editor, offerer.id)

    offer = get_offer_by_id(body.offer_id)

    stock = offers_api.create_stock(
        offer=offer,
        price=body.price,
        quantity=body.quantity,
        beginning=body.beginning_datetime,
        booking_limit_datetime=body.booking_limit_datetime,
    )

    return StockResponseIdModel.from_orm(stock)


@private_api.route("/stocks/<stock_id>", methods=["PATCH"])
@login_or_api_key_required
@spectree_serialize(response_model=StockResponseIdModel)
def edit_stock(stock_id: str, body: StockEditionBodyModel) -> StockResponseIdModel:
    stock = Stock.queryNotSoftDeleted().filter_by(id=dehumanize(stock_id)).join(Offer, VenueSQLEntity).first_or_404()

    offerer_id = stock.offer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)

    stock = offers_api.edit_stock(
        stock,
        price=body.price,
        quantity=body.quantity,
        beginning=body.beginning_datetime,
        booking_limit_datetime=body.booking_limit_datetime,
    )

    return StockResponseIdModel.from_orm(stock)


@private_api.route("/stocks/<id>", methods=["DELETE"])
@login_or_api_key_required
@spectree_serialize(response_model=StockResponseIdModel)
def delete_stock(id: str) -> StockResponseIdModel:
    # fmt: off
    stock = (
        Stock.queryNotSoftDeleted()
        .filter_by(id=dehumanize(id))
        .join(Offer, VenueSQLEntity)
        .first_or_404()
    )
    # fmt: on

    offerer_id = stock.offer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)

    offers_api.delete_stock(stock)

    return StockResponseIdModel.from_orm(stock)
