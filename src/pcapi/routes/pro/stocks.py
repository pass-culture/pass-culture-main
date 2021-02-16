from flask_login import current_user

import pcapi.core.offers.api as offers_api
from pcapi.core.offers.repository import get_stocks_for_offer
from pcapi.flask_app import private_api
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models import Venue
from pcapi.repository import offerer_queries
from pcapi.routes.serialization.stock_serialize import StockIdResponseModel
from pcapi.routes.serialization.stock_serialize import StockIdsResponseModel
from pcapi.routes.serialization.stock_serialize import StockResponseModel
from pcapi.routes.serialization.stock_serialize import StocksResponseModel
from pcapi.routes.serialization.stock_serialize import StocksUpsertBodyModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import login_or_api_key_required


@private_api.route("/offers/<offer_id>/stocks", methods=["GET"])
@login_or_api_key_required
@spectree_serialize(response_model=StocksResponseModel)
def get_stocks(offer_id: str) -> StocksResponseModel:
    offerer = offerer_queries.get_by_offer_id(dehumanize(offer_id))
    check_user_has_access_to_offerer(current_user, offerer.id)

    stocks = get_stocks_for_offer(dehumanize(offer_id))
    return StocksResponseModel(
        stocks=[StockResponseModel.from_orm(stock) for stock in stocks],
    )


@private_api.route("/stocks/bulk", methods=["POST"])
@login_or_api_key_required
@spectree_serialize(on_success_status=201, response_model=StockIdsResponseModel)
def upsert_stocks(body: StocksUpsertBodyModel) -> StockIdsResponseModel:
    offerer = offerer_queries.get_by_offer_id(body.offer_id)
    check_user_has_access_to_offerer(current_user, offerer.id)

    stocks = offers_api.upsert_stocks(body.offer_id, body.stocks)
    return StockIdsResponseModel(
        stockIds=[StockIdResponseModel.from_orm(stock) for stock in stocks],
    )


@private_api.route("/stocks/<stock_id>", methods=["DELETE"])
@login_or_api_key_required
@spectree_serialize(response_model=StockIdResponseModel)
def delete_stock(stock_id: str) -> StockIdResponseModel:
    # fmt: off
    stock = (
        Stock.queryNotSoftDeleted()
            .filter_by(id=dehumanize(stock_id))
            .join(Offer, Venue)
            .first_or_404()
    )
    # fmt: on

    offerer_id = stock.offer.venue.managingOffererId
    check_user_has_access_to_offerer(current_user, offerer_id)

    offers_api.delete_stock(stock)

    return StockIdResponseModel.from_orm(stock)
