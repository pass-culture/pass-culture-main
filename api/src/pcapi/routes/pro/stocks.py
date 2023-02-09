import logging

from flask_login import current_user
from flask_login import login_required
import sqlalchemy.orm as sqla_orm

from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers.models import Venue
import pcapi.core.offerers.repository as offerers_repository
from pcapi.core.offers import exceptions as offers_exceptions
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.repository as offers_repository
import pcapi.core.offers.validation as offers_validation
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import transaction
from pcapi.routes.apis import private_api
from pcapi.routes.public.books_stocks import serialization
from pcapi.serialization import utils as serialization_utils
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import check_user_has_access_to_offerer

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offers/<offer_id>/stocks", methods=["GET"])
@login_required
@spectree_serialize(response_model=serialization.StocksResponseModel, api=blueprint.pro_private_schema)
def get_stocks(offer_id: str) -> serialization.StocksResponseModel:
    try:
        offerer = offerers_repository.get_by_offer_id(dehumanize(offer_id))  # type: ignore [arg-type]
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)
    stocks = offers_repository.get_stocks_for_offer(dehumanize(offer_id))  # type: ignore [arg-type]
    return serialization.StocksResponseModel(
        stocks=[serialization.StockResponseModel.from_orm(stock) for stock in stocks],
    )


def _get_existing_stocks(
    offer_id: int, stocks_payload: list[serialization.StockEditionBodyModel]
) -> dict[int, offers_models.Stock]:
    existing_stocks = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offer_id,
        offers_models.Stock.id.in_([stock_payload.id for stock_payload in stocks_payload]),
    ).all()
    return {existing_stocks.id: existing_stocks for existing_stocks in existing_stocks}


@private_api.route("/stocks/bulk", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201, response_model=serialization.StocksResponseModel, api=blueprint.pro_private_schema
)
def upsert_stocks(body: serialization.StocksUpsertBodyModel) -> serialization.StocksResponseModel:
    try:
        offerer = offerers_repository.get_by_offer_id(body.offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    offer = (
        offers_models.Offer.query.options(
            sqla_orm.joinedload(offers_models.Offer.priceCategories),
        )
        .filter_by(id=body.offer_id)
        .one()
    )

    stocks_to_edit = [stock for stock in body.stocks if isinstance(stock, serialization.StockEditionBodyModel)]
    stocks_to_create = [stock for stock in body.stocks if isinstance(stock, serialization.StockCreationBodyModel)]
    if stocks_to_edit:
        existing_stocks = _get_existing_stocks(body.offer_id, stocks_to_edit)

    price_categories = {price_category.id: price_category for price_category in offer.priceCategories}

    upserted_stocks = []
    edited_stocks_with_update_info: list[tuple[offers_models.Stock, bool]] = []
    try:
        with transaction():
            for stock_to_edit in stocks_to_edit:
                if stock_to_edit.id not in existing_stocks:
                    raise ApiErrors(
                        {"stock_id": ["Le stock avec l'id %s n'existe pas" % stock_to_edit.id]}, status_code=400
                    )
                offers_validation.check_stock_has_price_or_price_category(offer, stock_to_edit, price_categories)

                edited_stock, is_beginning_updated = offers_api.edit_stock(
                    existing_stocks[stock_to_edit.id],
                    price=stock_to_edit.price,
                    quantity=stock_to_edit.quantity,
                    beginning_datetime=serialization_utils.as_utc_without_timezone(stock_to_edit.beginning_datetime)
                    if stock_to_edit.beginning_datetime
                    else None,
                    booking_limit_datetime=serialization_utils.as_utc_without_timezone(
                        stock_to_edit.booking_limit_datetime
                    )
                    if stock_to_edit.booking_limit_datetime
                    else None,
                    price_category=price_categories.get(stock_to_edit.price_category_id, None),
                )
                upserted_stocks.append(edited_stock)
                edited_stocks_with_update_info.append((edited_stock, is_beginning_updated))

            for stock_to_create in stocks_to_create:
                offers_validation.check_stock_has_price_or_price_category(offer, stock_to_create, price_categories)
                created_stock = offers_api.create_stock(
                    offer,
                    price=stock_to_create.price,
                    activation_codes=stock_to_create.activation_codes,
                    activation_codes_expiration_datetime=stock_to_create.activation_codes_expiration_datetime,
                    quantity=stock_to_create.quantity,
                    beginning_datetime=stock_to_create.beginning_datetime,
                    booking_limit_datetime=stock_to_create.booking_limit_datetime,
                    price_category=price_categories.get(stock_to_create.price_category_id, None),
                )
                upserted_stocks.append(created_stock)

    except offers_exceptions.BookingLimitDatetimeTooLate:
        raise ApiErrors(
            {"stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]},
            status_code=400,
        )
    offers_api.handle_stocks_edition(body.offer_id, edited_stocks_with_update_info)

    return serialization.StocksResponseModel(
        stocks=[serialization.StockResponseModel.from_orm(stock) for stock in upserted_stocks]
    )


@private_api.route("/stocks/<stock_id>", methods=["DELETE"])
@login_required
@spectree_serialize(response_model=serialization.StockIdResponseModel, api=blueprint.pro_private_schema)
def delete_stock(stock_id: str) -> serialization.StockIdResponseModel:
    # fmt: off
    stock = (
        offers_models.Stock.queryNotSoftDeleted()
            .filter_by(id=dehumanize(stock_id))
            .join(offers_models.Offer, Venue)
            .first_or_404()
    )
    # fmt: on

    offerer_id = stock.offer.venue.managingOffererId
    check_user_has_access_to_offerer(current_user, offerer_id)

    offers_api.delete_stock(stock)

    return serialization.StockIdResponseModel.from_orm(stock)
