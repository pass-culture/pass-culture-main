import logging

from flask_login import current_user
from flask_login import login_required
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers.models import Venue
import pcapi.core.offerers.repository as offerers_repository
from pcapi.core.offers import exceptions as offers_exceptions
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.validation as offers_validation
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import transaction
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import stock_serialize
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


def _get_existing_stocks_by_fields(
    offer_id: int,
    stock_payload: list[stock_serialize.StockCreationBodyModel | stock_serialize.StockEditionBodyModel],
) -> list[offers_models.Stock]:
    combinaisons_to_check = [
        sa.and_(
            offers_models.Stock.offerId == offer_id,
            offers_models.Stock.isSoftDeleted == False,
            offers_models.Stock.beginningDatetime == stock.beginning_datetime,
            offers_models.Stock.priceCategoryId == stock.price_category_id,
        )
        for stock in stock_payload
    ]
    return db.session.query(offers_models.Stock).filter(sa.or_(*combinaisons_to_check)).all()


def _find_offer_matching_event_stocks(
    offer_id: int,
    stocks_payload: stock_serialize.EventStocksList,
) -> list[offers_models.Stock]:
    combinaisons_to_check = [
        sa.and_(
            offers_models.Stock.offerId == offer_id,
            offers_models.Stock.isSoftDeleted == False,
            offers_models.Stock.beginningDatetime == stock.beginning_datetime,
            offers_models.Stock.priceCategoryId == stock.price_category_id,
        )
        for stock in stocks_payload
    ]
    return offers_models.Stock.query.filter(sa.or_(*combinaisons_to_check)).all()


def _get_existing_stocks_by_id(
    offer_id: int,
    stocks_payload: list[stock_serialize.StockEditionBodyModel] | list[stock_serialize.EventStockUpdateBodyModel],
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
    offer: offers_models.Offer = offers_models.Offer.query.get_or_404(body.offer_id)
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
    stock: offers_models.Stock = offers_models.Stock.query.get_or_404(stock_id)
    check_user_has_access_to_offerer(current_user, stock.offer.venue.managingOffererId)
    offers_api.edit_stock(stock, **body.dict())
    return stock_serialize.StockIdResponseModel.from_orm(stock)


@private_api.route("/stocks/bulk_create", methods=["POST"])
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
    offer: offers_models.Offer = offers_models.Offer.query.options(
        sa_orm.joinedload(offers_models.Offer.priceCategories)
    ).get_or_404(body.offer_id)
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
    except offers_exceptions.OfferEditionBaseException as error:
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
    offer: offers_models.Offer = offers_models.Offer.query.options(
        sa_orm.joinedload(offers_models.Offer.priceCategories)
    ).get_or_404(body.offer_id)
    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    # Step 1 : Filter out duplicated stocks
    stocks_to_edit = _filter_out_stock_duplicates(body.stocks, offer.id)

    # Step 2 : Check price
    offers_validation.check_stocks_price(stocks_to_edit, offer)

    # Step 3 : Bulk update
    edited_stocks_count = 0
    existing_stocks = _get_existing_stocks_by_id(body.offer_id, stocks_to_edit)
    price_categories = {price_category.id: price_category for price_category in offer.priceCategories}
    stocks_with_edited_beginning_datetime = []

    try:
        with transaction():
            for stock in stocks_to_edit:
                if stock.id not in existing_stocks:
                    raise api_errors.ApiErrors({"stock_id": ["Le stock avec l'id %s n'existe pas" % stock.id]})

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
    except offers_exceptions.OfferEditionBaseException as error:
        raise api_errors.ApiErrors(error.errors)

    # Done once we are sure all stocks have been successfully edited
    for edited_stock in stocks_with_edited_beginning_datetime:
        assert edited_stock  # to make mypy happy
        offers_api.handle_event_stock_beginning_datetime_update(edited_stock)

    return stock_serialize.StocksResponseModel(stocks_count=edited_stocks_count)


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
        raise api_errors.ResourceNotFoundError({"offerer": ["Aucune structure trouvée à partir de cette offre"]})
    check_user_has_access_to_offerer(current_user, offerer.id)

    offer = (
        db.session.query(offers_models.Offer)
        .options(
            sa_orm.joinedload(offers_models.Offer.priceCategories),
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
    offers_validation.check_stocks_count_with_previous_offer_stock(stocks_to_create, offer)

    price_categories = {price_category.id: price_category for price_category in offer.priceCategories}

    upserted_stocks = []
    edited_stocks_with_update_info: list[tuple[offers_models.Stock, bool]] = []
    try:
        with transaction():
            if stocks_to_edit:
                existing_stocks = _get_existing_stocks_by_id(body.offer_id, stocks_to_edit)
                for stock_to_edit in stocks_to_edit:
                    if stock_to_edit.id not in existing_stocks:
                        raise api_errors.ApiErrors(
                            {"stock_id": ["Le stock avec l'id %s n'existe pas" % stock_to_edit.id]},
                        )

                    offers_validation.check_stock_has_price_or_price_category(offer, stock_to_edit, price_categories)

                    edited_stock, is_beginning_updated = offers_api.edit_stock(
                        existing_stocks[stock_to_edit.id],
                        price=stock_to_edit.price,
                        quantity=stock_to_edit.quantity,
                        beginning_datetime=stock_to_edit.beginning_datetime,
                        booking_limit_datetime=stock_to_edit.booking_limit_datetime,
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
        raise api_errors.ApiErrors(
            {"stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]},
        )
    except offers_exceptions.OfferEditionBaseException as error:
        raise api_errors.ApiErrors(error.errors)

    try:
        offers_api.handle_stocks_edition(edited_stocks_with_update_info)
    except booking_exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"booking": ["Cette réservation a été annulée"]})
    except booking_exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ResourceGoneError({"payment": ["Le remboursement est en cours de traitement"]})
    except booking_exceptions.BookingHasActivationCode:
        raise api_errors.ForbiddenError({"booking": ["Cette réservation ne peut pas être marquée comme inutilisée"]})
    except booking_exceptions.BookingIsNotUsed:
        raise api_errors.ResourceGoneError({"booking": ["Cette contremarque n'a pas encore été validée"]})

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
        raise api_errors.ApiErrors(error.errors)
    return stock_serialize.StockIdResponseModel.from_orm(stock)
