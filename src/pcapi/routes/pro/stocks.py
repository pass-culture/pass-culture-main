from typing import List

from flask_login import current_user
from flask_login import login_required

from pcapi.core.offerers.models import Offerer
import pcapi.core.offers.api as offers_api
from pcapi.core.offers.repository import get_stocks_for_offer
from pcapi.core.providers.models import StockDetail
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models import Venue
from pcapi.repository import offerer_queries
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.stock_serialize import StockIdResponseModel
from pcapi.routes.serialization.stock_serialize import StockIdsResponseModel
from pcapi.routes.serialization.stock_serialize import StockResponseModel
from pcapi.routes.serialization.stock_serialize import StocksResponseModel
from pcapi.routes.serialization.stock_serialize import StocksUpsertBodyModel
from pcapi.routes.serialization.stock_serialize import UpdateVenueStockBodyModel
from pcapi.routes.serialization.stock_serialize import UpdateVenueStocksBodyModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.custom_keys import compute_venue_reference
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.workers.synchronize_stocks_job import synchronize_stocks_job

from .blueprints import api
from .blueprints import pro_api_v2


@private_api.route("/offers/<offer_id>/stocks", methods=["GET"])
@login_required
@spectree_serialize(response_model=StocksResponseModel)
def get_stocks(offer_id: str) -> StocksResponseModel:
    offerer = offerer_queries.get_by_offer_id(dehumanize(offer_id))
    check_user_has_access_to_offerer(current_user, offerer.id)

    stocks = get_stocks_for_offer(dehumanize(offer_id))
    return StocksResponseModel(
        stocks=[StockResponseModel.from_orm(stock) for stock in stocks],
    )


@private_api.route("/stocks/bulk", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=StockIdsResponseModel)
def upsert_stocks(body: StocksUpsertBodyModel) -> StockIdsResponseModel:
    offerer = offerer_queries.get_by_offer_id(body.offer_id)
    check_user_has_access_to_offerer(current_user, offerer.id)

    stocks = offers_api.upsert_stocks(body.offer_id, body.stocks, current_user)
    return StockIdsResponseModel(
        stockIds=[StockIdResponseModel.from_orm(stock) for stock in stocks],
    )


@private_api.route("/stocks/<stock_id>", methods=["DELETE"])
@login_required
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


@pro_api_v2.route("/venue/<int:venue_id>/stocks", methods=["POST"])
@api_key_required
@spectree_serialize(on_success_status=204, on_error_statuses=[401, 404], api=api, tags=["API Stocks"])
def update_stocks(venue_id: int, body: UpdateVenueStocksBodyModel) -> None:
    # in French, to be used by Swagger for the API documentation
    """Mise à jour des stocks d'un lieu enregistré auprès du pass Culture.

    Seuls les livres, préalablement présents dans le catalogue du pass Culture seront pris en compte, tous les autres stocks
    seront filtrés.

    Les stocks sont référencés par leur isbn au format EAN13.

    Le champ "available" représente la quantité de stocks disponible en librairie.
    Le champ "price" (optionnel) correspond au prix en euros.

    Le paramètre {venue_id} correspond à un lieu qui doit être attaché à la structure à laquelle la clé d'API utilisée est reliée.
    """
    offerer_id = current_api_key.offererId
    venue = Venue.query.join(Offerer).filter(Venue.id == venue_id, Offerer.id == offerer_id).first_or_404()

    stock_details = _build_stock_details_from_body(body.stocks, venue.id)
    synchronize_stocks_job.delay(stock_details, venue.id)


def _build_stock_details_from_body(raw_stocks: List[UpdateVenueStockBodyModel], venue_id: int):
    stock_details = {}
    for stock in raw_stocks:
        stock_details[stock.ref] = StockDetail(
            products_provider_reference=stock.ref,
            offers_provider_reference=compute_venue_reference(stock.ref, venue_id),
            stocks_provider_reference=compute_venue_reference(stock.ref, venue_id),
            venue_reference=compute_venue_reference(stock.ref, venue_id),
            available_quantity=stock.available,
            price=stock.price,
        )

    return list(stock_details.values())
