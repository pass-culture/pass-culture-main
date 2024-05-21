import logging

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
from pcapi.routes.public.books_stocks import serialization
from pcapi.serialization import utils as serialization_utils
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer

from . import blueprint


logger = logging.getLogger(__name__)


def _stock_exists(
    stock_data: serialization.StockCreationBodyModel | serialization.StockEditionBodyModel,
    existing_stocks: list[offers_models.Stock],
) -> bool:
    for stock in existing_stocks:
        if (
            (stock.id != stock_data.id if isinstance(stock_data, serialization.StockEditionBodyModel) else True)
            and stock.beginningDatetime
            == (stock_data.beginning_datetime.replace(tzinfo=None) if stock_data.beginning_datetime else None)
            and stock.priceCategoryId == stock_data.price_category_id
            and (stock.price == stock_data.price if not stock.priceCategoryId else True)
        ):
            return True
    return False


def _get_existing_stocks_by_fields(
    offer_id: int,
    stock_payload: list[serialization.StockCreationBodyModel | serialization.StockEditionBodyModel],
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
    offer_id: int, stocks_payload: list[serialization.StockEditionBodyModel]
) -> dict[int, offers_models.Stock]:
    existing_stocks = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offer_id,
        offers_models.Stock.isSoftDeleted == False,
        offers_models.Stock.id.in_([stock_payload.id for stock_payload in stocks_payload]),
    ).all()
    return {existing_stocks.id: existing_stocks for existing_stocks in existing_stocks}


def _get_number_of_existing_stocks(offer_id: int) -> int:
    return (
        offers_models.Stock.query.filter_by(offerId=offer_id).filter(offers_models.Stock.isSoftDeleted == False).count()
    )


@private_api.route("/stocks/bulk", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=serialization.StocksResponseModel,
    api=blueprint.pro_private_schema,
)
def upsert_stocks(
    body: serialization.StocksUpsertBodyModel,
) -> serialization.StocksResponseModel:
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
        if (isinstance(stock, serialization.StockEditionBodyModel) and not _stock_exists(stock, matching_stocks))
    ]
    stocks_to_create = [
        stock
        for stock in body.stocks
        if (isinstance(stock, serialization.StockCreationBodyModel) and not _stock_exists(stock, matching_stocks))
    ]

    offers_validation.check_stocks_price(stocks_to_edit, offer)
    offers_validation.check_stocks_price(stocks_to_create, offer)
    if stocks_to_create:
        number_of_existing_stocks = _get_number_of_existing_stocks(body.offer_id)
        if number_of_existing_stocks + len(stocks_to_create) > offers_models.Offer.MAX_STOCKS_PER_OFFER:
            raise ApiErrors(
                {
                    "stocks": [
                        "Le nombre maximum de stocks par offre est de %s" % offers_models.Offer.MAX_STOCKS_PER_OFFER
                    ]
                },
                status_code=400,
            )

    price_categories = {price_category.id: price_category for price_category in offer.priceCategories}

    upserted_stocks = []
    edited_stocks_with_update_info: list[tuple[offers_models.Stock, bool]] = []
    try:
        with transaction():
            if stocks_to_edit:
                existing_stocks = _get_existing_stocks_by_id(body.offer_id, stocks_to_edit)
                for stock_to_edit in stocks_to_edit:
                    if stock_to_edit.id not in existing_stocks:
                        raise ApiErrors(
                            {"stock_id": ["Le stock avec l'id %s n'existe pas" % stock_to_edit.id]},
                            status_code=400,
                        )

                    offers_validation.check_stock_has_price_or_price_category(offer, stock_to_edit, price_categories)

                    edited_stock, is_beginning_updated = offers_api.edit_stock(
                        existing_stocks[stock_to_edit.id],
                        price=stock_to_edit.price,
                        quantity=stock_to_edit.quantity,
                        beginning_datetime=(
                            serialization_utils.as_utc_without_timezone(stock_to_edit.beginning_datetime)
                            if stock_to_edit.beginning_datetime
                            else None
                        ),
                        booking_limit_datetime=(
                            serialization_utils.as_utc_without_timezone(stock_to_edit.booking_limit_datetime)
                            if stock_to_edit.booking_limit_datetime
                            else None
                        ),
                        price_category=price_categories.get(stock_to_edit.price_category_id, None),
                    )
                    if edited_stock:
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
    except offers_exceptions.OfferEditionBaseException as error:
        raise ApiErrors(error.errors, status_code=400)

    try:
        offers_api.handle_stocks_edition(edited_stocks_with_update_info)
    except booking_exceptions.BookingIsAlreadyCancelled:
        raise ResourceGoneError({"booking": ["Cette réservation a été annulée"]})
    except booking_exceptions.BookingIsAlreadyRefunded:
        raise ResourceGoneError({"payment": ["Le remboursement est en cours de traitement"]})
    except booking_exceptions.BookingHasActivationCode:
        raise ForbiddenError({"booking": ["Cette réservation ne peut pas être marquée comme inutilisée"]})
    except booking_exceptions.BookingIsNotUsed:
        raise ResourceGoneError({"booking": ["Cette contremarque n'a pas encore été validée"]})

    return serialization.StocksResponseModel(stocks_count=len(upserted_stocks))


@private_api.route("/stocks/<int:stock_id>", methods=["DELETE"])
@login_required
@spectree_serialize(response_model=serialization.StockIdResponseModel, api=blueprint.pro_private_schema)
def delete_stock(stock_id: int) -> serialization.StockIdResponseModel:
    # fmt: off
    stock = (
        offers_models.Stock.queryNotSoftDeleted()
            .filter_by(id=stock_id)
            .join(offers_models.Offer, Venue)
            .first_or_404()
    )
    # fmt: on

    offerer_id = stock.offer.venue.managingOffererId
    check_user_has_access_to_offerer(current_user, offerer_id)
    try:
        offers_api.delete_stock(stock)
    except offers_exceptions.OfferEditionBaseException as error:
        raise ApiErrors(error.errors, status_code=400)
    return serialization.StockIdResponseModel.from_orm(stock)
