import logging

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask_login import current_user
from flask_login import login_required

import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.validation as offers_validation
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.utils import first_or_404
from pcapi.models.utils import get_or_404
from pcapi.models.utils import get_or_404_from_query
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import stock_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.repository import transaction
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.transaction_manager import atomic

from . import blueprint


logger = logging.getLogger(__name__)


def _stock_already_exists(
    stock_data: stock_serialize.EventStockCreateBodyModel | stock_serialize.EventStockUpdateBodyModel,
    existing_stocks: list[offers_models.Stock],
) -> bool:
    return any(
        (
            stock.beginningDatetime == stock_data.beginning_datetime.replace(tzinfo=None)
            and stock.priceCategoryId == stock_data.price_category_id
            and (not hasattr(stock_data, "id") or stock.id != stock_data.id)
        )
        for stock in existing_stocks
    )


def _find_offer_matching_event_stocks(
    offer_id: int,
    stocks_payload: stock_serialize.EventStocksList,
) -> list[offers_models.Stock]:
    combinaisons_to_check = [
        sa.and_(
            offers_models.Stock.offerId == offer_id,
            offers_models.Stock.isSoftDeleted.is_(False),
            offers_models.Stock.beginningDatetime == stock.beginning_datetime,
            offers_models.Stock.priceCategoryId == stock.price_category_id,
        )
        for stock in stocks_payload
    ]
    return db.session.query(offers_models.Stock).filter(sa.or_(*combinaisons_to_check)).all()


def _get_existing_stocks_by_id(
    offer_id: int,
    stocks_payload: list[stock_serialize.EventStockUpdateBodyModel],
) -> dict[int, offers_models.Stock]:
    existing_stocks = (
        db.session.query(offers_models.Stock)
        .filter(
            offers_models.Stock.offerId == offer_id,
            offers_models.Stock.isSoftDeleted == False,
            offers_models.Stock.id.in_([stock_payload.id for stock_payload in stocks_payload]),
        )
        .all()
    )
    return {existing_stocks.id: existing_stocks for existing_stocks in existing_stocks}


def _filter_out_stock_duplicates(
    stocks_list: stock_serialize.EventStocksList, offer_id: int
) -> stock_serialize.EventStocksList:
    matching_event_stocks = _find_offer_matching_event_stocks(offer_id=offer_id, stocks_payload=stocks_list)

    if matching_event_stocks:
        return list(filter(lambda stock: not _stock_already_exists(stock, matching_event_stocks), stocks_list))

    return stocks_list


@private_api.route("/stocks", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=stock_serialize.StockIdResponseModel,
    api=blueprint.pro_private_schema,
)
@atomic()
def create_thing_stock(body: stock_serialize.ThingStockCreateBodyModel) -> stock_serialize.StockIdResponseModel:
    offer: offers_models.Offer = get_or_404(offers_models.Offer, body.offer_id)
    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)
    input_data = body.dict()
    input_data.pop("offer_id")
    stock = offers_api.create_stock(offer, **input_data)
    return stock_serialize.StockIdResponseModel.from_orm(stock)


@private_api.route("/stocks/<int:stock_id>", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=200,
    response_model=stock_serialize.StockIdResponseModel,
    api=blueprint.pro_private_schema,
)
@atomic()
def update_thing_stock(
    stock_id: int,
    body: stock_serialize.ThingStockUpdateBodyModel,
) -> stock_serialize.StockIdResponseModel:
    stock: offers_models.Stock = get_or_404(offers_models.Stock, stock_id)
    check_user_has_access_to_offerer(current_user, stock.offer.venue.managingOffererId)
    offers_api.edit_stock(stock, **body.dict(exclude_unset=True))
    return stock_serialize.StockIdResponseModel.from_orm(stock)


@private_api.route("/stocks/bulk", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=stock_serialize.StocksResponseModel,
    api=blueprint.pro_private_schema,
)
@atomic()
def bulk_create_event_stocks(
    body: stock_serialize.EventStocksBulkCreateBodyModel,
) -> stock_serialize.StocksResponseModel:
    offer: offers_models.Offer = get_or_404_from_query(
        db.session.query(offers_models.Offer).options(sa_orm.joinedload(offers_models.Offer.priceCategories)),
        body.offer_id,
    )
    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    # Step 1 : Filter out existing stocks
    stocks_to_create = _filter_out_stock_duplicates(body.stocks, offer.id)

    # Step 2 : Check price
    offers_validation.check_stocks_price(stocks_to_create, offer)
    offers_validation.check_stocks_count_with_previous_offer_stock(stocks_to_create, offer)

    # Step 3 : Bulk create
    created_stocks_count = 0
    price_categories = {price_category.id: price_category for price_category in offer.priceCategories}
    try:
        for stock in stocks_to_create:
            offers_api.create_stock(
                offer,
                quantity=stock.quantity,
                beginning_datetime=stock.beginning_datetime,
                booking_limit_datetime=stock.booking_limit_datetime,
                price_category=price_categories[stock.price_category_id],
            )
            created_stocks_count += 1
    except offers_exceptions.BookingLimitDatetimeTooLate:
        raise api_errors.ApiErrors(
            {"stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]},
        )
    except offers_exceptions.OfferException as error:
        raise api_errors.ApiErrors(error.errors)

    return stock_serialize.StocksResponseModel(stocks_count=created_stocks_count)


@private_api.route("/stocks/bulk", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=200,
    response_model=stock_serialize.StocksResponseModel,
    api=blueprint.pro_private_schema,
)
@atomic()
def bulk_update_event_stocks(
    body: stock_serialize.EventStocksBulkUpdateBodyModel,
) -> stock_serialize.StocksResponseModel:
    offer: offers_models.Offer = get_or_404_from_query(
        db.session.query(offers_models.Offer).options(sa_orm.joinedload(offers_models.Offer.priceCategories)),
        body.offer_id,
    )
    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    # Step 1 : Filter out duplicated stocks
    stocks_to_edit = _filter_out_stock_duplicates(body.stocks, offer.id)

    # Step 2 : Check price
    offers_validation.check_stocks_price(stocks_to_edit, offer)

    # Step 3 : Bulk update
    edited_stocks_count = 0
    existing_stocks = _get_existing_stocks_by_id(body.offer_id, stocks_to_edit)
    missing_stocks_ids = {stock.id for stock in stocks_to_edit} - set(existing_stocks.keys())
    if missing_stocks_ids:
        raise api_errors.ApiErrors(
            {
                "stock_id": [
                    "Pas de stocks avec les ids: %s" % ", ".join(str(stock_id) for stock_id in missing_stocks_ids)
                ]
            }
        )
    price_categories = {price_category.id: price_category for price_category in offer.priceCategories}
    stocks_with_edited_beginning_datetime = []

    try:
        with transaction():
            for stock in stocks_to_edit:
                edited_stock, is_beginning_updated = offers_api.edit_stock(
                    existing_stocks[stock.id],
                    quantity=stock.quantity,
                    beginning_datetime=stock.beginning_datetime,
                    price_category=price_categories[stock.price_category_id],
                    booking_limit_datetime=stock.booking_limit_datetime or stock.beginning_datetime,
                )
                if edited_stock:
                    edited_stocks_count += 1
                if is_beginning_updated:
                    stocks_with_edited_beginning_datetime.append(edited_stock)
    except offers_exceptions.BookingLimitDatetimeTooLate:
        raise api_errors.ApiErrors(
            {"stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]},
        )
    except offers_exceptions.OfferException as error:
        raise api_errors.ApiErrors(error.errors)

    # Done once we are sure all stocks have been successfully edited
    for edited_stock in stocks_with_edited_beginning_datetime:
        assert edited_stock  # to make mypy happy
        offers_api.handle_event_stock_beginning_datetime_update(edited_stock)

    return stock_serialize.StocksResponseModel(stocks_count=edited_stocks_count)


@private_api.route("/stocks/<int:stock_id>", methods=["DELETE"])
@atomic()
@login_required
@spectree_serialize(response_model=stock_serialize.StockIdResponseModel, api=blueprint.pro_private_schema)
def delete_stock(stock_id: int) -> stock_serialize.StockIdResponseModel:
    stock = first_or_404(
        offers_models.Stock.queryNotSoftDeleted().filter_by(id=stock_id).join(offers_models.Offer).join(Venue)
    )

    offerer_id = stock.offer.venue.managingOffererId
    check_user_has_access_to_offerer(current_user, offerer_id)
    offers_api.delete_stock(stock, current_user.real_user.id, current_user.is_impersonated)

    return stock_serialize.StockIdResponseModel.from_orm(stock)
