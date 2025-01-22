import logging
from typing import Collection

from flask_login import current_user
from flask_login import login_required
from sqlalchemy import and_
from sqlalchemy import or_
import sqlalchemy.orm as sqla_orm

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers.models import Venue
import pcapi.core.offerers.repository as offerers_repository
from pcapi.core.offers import exceptions as offers_exceptions
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.validation as offers_validation
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import ResourceGoneError
from pcapi.repository import transaction
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import stock_serialize
from pcapi.serialization import utils as serialization_utils
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer

from . import blueprint


logger = logging.getLogger(__name__)


def _stock_exists(
    stock_data: stock_serialize.StockCreationBodyModel | stock_serialize.StockEditionBodyModel,
    existing_stocks: list[offers_models.Stock],
) -> bool:
    for stock in existing_stocks:
        if (
            (stock.id != stock_data.id if isinstance(stock_data, stock_serialize.StockEditionBodyModel) else True)
            and stock.beginningDatetime
            == (stock_data.beginning_datetime.replace(tzinfo=None) if stock_data.beginning_datetime else None)
            and stock.priceCategoryId == stock_data.price_category_id
            and (stock.price == stock_data.price if not stock.priceCategoryId else True)
        ):
            return True
    return False


def _get_existing_stocks_by_fields(
    offer_id: int,
    stock_payload: list[stock_serialize.StockCreationBodyModel | stock_serialize.StockEditionBodyModel],
) -> list[offers_models.Stock]:
    combinaisons_to_check = [
        and_(
            offers_models.Stock.offerId == offer_id,
            offers_models.Stock.isSoftDeleted == False,
            offers_models.Stock.beginningDatetime == stock.beginning_datetime,
            offers_models.Stock.priceCategoryId == stock.price_category_id,
        )
        for stock in stock_payload
    ]
    return offers_models.Stock.query.filter(or_(*combinaisons_to_check)).all()


def _get_existing_stocks_by_id(
    offer_id: int, stocks_payload: list[stock_serialize.StockEditionBodyModel]
) -> dict[int, offers_models.Stock]:
    existing_stocks = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offer_id,
        offers_models.Stock.isSoftDeleted == False,
        offers_models.Stock.id.in_([stock_payload.id for stock_payload in stocks_payload]),
    ).all()
    return {existing_stocks.id: existing_stocks for existing_stocks in existing_stocks}


def _edit_stocks(
    stocks: Collection[offers_models.Stock],
    offer: offers_models.Offer,
    price_categories: Collection[offers_models.PriceCategory],
) -> Collection[tuple[offers_models.Stock, bool]]:
    edited_stocks_with_update_info = []
    if not stocks:
        return edited_stocks_with_update_info

    existing_stocks = _get_existing_stocks_by_id(offer.id, stocks)
    for stock in stocks:
        if stock.id not in existing_stocks:
            raise ApiErrors(
                {"stock_id": ["Le stock avec l'id %s n'existe pas" % stock.id]},
                status_code=400,
            )

        edited_stock, is_beginning_updated = _edit_stock(
            stock=stock, existing_stocks=existing_stocks, offer=offer, price_categories=price_categories
        )

        if edited_stock:
            edited_stocks_with_update_info.append(edited_stock, is_beginning_updated)

    return edited_stocks_with_update_info


def _edit_stock(
    stock: offers_models.Stock,
    existing_stocks: Collection[offers_models.Stock],
    offer: offers_models.Offer,
    price_categories: Collection[offers_models.PriceCategory],
) -> tuple[offers_models.Stock, bool] | tuple[None, None]:
    offers_validation.check_stock_has_price_or_price_category(offer, stock, price_categories)

    try:
        edited_stock, is_beginning_updated = offers_api.edit_stock(
            existing_stocks[stock.id],
            price=stock.price,
            quantity=stock.quantity,
            beginning_datetime=(
                serialization_utils.as_utc_without_timezone(stock.beginning_datetime)
                if stock.beginning_datetime
                else None
            ),
            booking_limit_datetime=(
                serialization_utils.as_utc_without_timezone(stock.booking_limit_datetime)
                if stock.booking_limit_datetime
                else None
            ),
            price_category=price_categories.get(stock.price_category_id, None),
        )
    except offers_exceptions.BookingLimitDatetimeTooLate:
        errors = {
            "stocks": {
                stock.id: "La date limite de réservation ne peut être postérieure à la date de début de l'évènement",
            }
        }
        raise ApiErrors(errors, status_code=400)
    except offers_exceptions.OfferEditionBaseException as error:
        raise ApiErrors(error.errors, status_code=400)

    if edited_stock:
        return edited_stock, is_beginning_updated
    return None, None
    # upserted_stocks.append(edited_stock)
    # edited_stocks_with_update_info.append((edited_stock, is_beginning_updated))


def _create_stocks(
    stocks: Collection[offers_models.Stock],
    offer: offers_models.Offer,
    price_categories: Collection[offers_models.PriceCategory],
) -> Collection[offers_models.Stock]:
    upserted_stocks = []

    for stock_to_create in stocks:
        created_stock = _create_stock(stock_to_create, offer, price_categories)
        upserted_stocks.append(created_stock)

    return upserted_stocks


def _create_stock(
    stock: offers_models.Stock, offer: offers_models.Offer, price_categories: Collection[offers_models.PriceCategory]
) -> offers_models.Stock:
    offers_validation.check_stock_has_price_or_price_category(offer, stock, price_categories)

    try:
        created_stock = offers_api.create_stock(
            offer,
            price=stock.price,
            activation_codes=stock.activation_codes,
            activation_codes_expiration_datetime=stock.activation_codes_expiration_datetime,
            quantity=stock.quantity,
            beginning_datetime=stock.beginning_datetime,
            booking_limit_datetime=stock.booking_limit_datetime,
            price_category=price_categories.get(stock.price_category_id, None),
        )
    except offers_exceptions.BookingLimitDatetimeTooLate:
        errors = {
            "stocks": {
                stock.id: "La date limite de réservation ne peut être postérieure à la date de début de l'évènement",
            }
        }
        raise ApiErrors(errors, status_code=400)

    return created_stock


@private_api.route("/stocks/bulk", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=stock_serialize.StocksResponseModel,
    api=blueprint.pro_private_schema,
)
def upsert_stocks(body: stock_serialize.StocksUpsertBodyModel) -> stock_serialize.StocksResponseModel:
    try:
        offerer = offerers_repository.get_by_offer_id(body.offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors(
            {"offerer": ["Aucune structure trouvée à partir de cette offre"]},
            status_code=404,
        )
    check_user_has_access_to_offerer(current_user, offerer.id)

    offer = (
        offers_models.Offer.query.options(
            sqla_orm.joinedload(offers_models.Offer.priceCategories),
        )
        .filter_by(id=body.offer_id)
        .one()
    )

    matching_stocks = _get_existing_stocks_by_fields(body.offer_id, body.stocks)
    stocks_to_edit = [
        stock
        for stock in body.stocks
        if (isinstance(stock, stock_serialize.StockEditionBodyModel) and not _stock_exists(stock, matching_stocks))
    ]
    stocks_to_create = [
        stock
        for stock in body.stocks
        if (isinstance(stock, stock_serialize.StockCreationBodyModel) and not _stock_exists(stock, matching_stocks))
    ]

    offers_validation.check_stocks_price(stocks_to_edit, offer)
    offers_validation.check_stocks_price(stocks_to_create, offer)
    offers_validation.check_stocks_quantity_with_previous_offer_stock(stocks_to_create, offer)

    price_categories = {price_category.id: price_category for price_category in offer.priceCategories}

    upserted_stocks = []
    edited_stocks_with_update_info: list[tuple[offers_models.Stock, bool]] = []

    with transaction():
        edited_stocks_info = _edit_stocks(stocks_to_edit, offer, price_categories)
        if edited_stocks_info:
            upserted_stocks.extend([row[0] for row in edited_stocks_info])
            edited_stocks_with_update_info.extend(edited_stocks_info)

        upserted_stocks.extend(_create_stocks(stocks_to_create, offer, price_categories))

    for stock, is_beginning_datetime_updated in edited_stocks_with_update_info:
        try:
            offers_api.handle_stock_edition(stock, is_beginning_datetime_updated)
        except booking_exceptions.BookingIsAlreadyCancelled:
            raise ResourceGoneError({"booking": {stock.id: ["Cette réservation a été annulée"]}})
        except booking_exceptions.BookingIsAlreadyRefunded:
            raise ResourceGoneError({"payment": {stock.id: ["Le remboursement est en cours de traitement"]}})
        except booking_exceptions.BookingHasActivationCode:
            raise ForbiddenError(
                {"booking": {stock.id: ["Cette réservation ne peut pas être marquée comme inutilisée"]}}
            )
        except booking_exceptions.BookingIsNotUsed:
            raise ResourceGoneError({"booking": {stock.id: ["Cette contremarque n'a pas encore été validée"]}})

    return stock_serialize.StocksResponseModel(stocks_count=len(upserted_stocks))


@private_api.route("/stocks/<int:stock_id>", methods=["DELETE"])
@login_required
@spectree_serialize(response_model=stock_serialize.StockIdResponseModel, api=blueprint.pro_private_schema)
def delete_stock(stock_id: int) -> stock_serialize.StockIdResponseModel:
    # fmt: off
    stock = (
        offers_models.Stock.queryNotSoftDeleted()
            .filter_by(id=stock_id)
            .join(offers_models.Offer).join(Venue)
            .first_or_404()
    )
    # fmt: on

    offerer_id = stock.offer.venue.managingOffererId
    check_user_has_access_to_offerer(current_user, offerer_id)
    try:
        offers_api.delete_stock(stock, current_user.real_user.id, current_user.is_impersonated)
    except offers_exceptions.OfferEditionBaseException as error:
        raise ApiErrors(error.errors, status_code=400)
    return stock_serialize.StockIdResponseModel.from_orm(stock)
