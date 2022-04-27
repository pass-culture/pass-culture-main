import logging
from typing import List

from flask_login import current_user
from flask_login import login_required
from sqlalchemy import exc
from sqlalchemy.orm.exc import MultipleResultsFound as SQLAMultipleResultsFound

from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
import pcapi.core.offerers.repository as offerers_repository
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import repository as offers_repository
import pcapi.core.offers.api as offers_api
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.repository import get_stocks_for_offer
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import offers_serialize
from pcapi.routes.serialization import stock_serialize
from pcapi.routes.serialization.stock_serialize import EducationalStockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import EducationalStockEditionBodyModel
from pcapi.routes.serialization.stock_serialize import StockIdResponseModel
from pcapi.routes.serialization.stock_serialize import StockIdsResponseModel
from pcapi.routes.serialization.stock_serialize import StockResponseModel
from pcapi.routes.serialization.stock_serialize import StocksResponseModel
from pcapi.routes.serialization.stock_serialize import StocksUpsertBodyModel
from pcapi.routes.serialization.stock_serialize import UpdateVenueStockBodyModel
from pcapi.routes.serialization.stock_serialize import UpdateVenueStocksBodyModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.workers.synchronize_stocks_job import synchronize_stocks_job

from . import blueprint
from ...models import db


logger = logging.getLogger(__name__)


@private_api.route("/offers/<offer_id>/stocks", methods=["GET"])
@login_required
@spectree_serialize(response_model=StocksResponseModel, api=blueprint.pro_private_schema)
def get_stocks(offer_id: str) -> StocksResponseModel:
    try:
        offerer = offerers_repository.get_by_offer_id(dehumanize(offer_id))  # type: ignore [arg-type]
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)
    stocks = get_stocks_for_offer(dehumanize(offer_id))  # type: ignore [arg-type]
    return StocksResponseModel(
        stocks=[StockResponseModel.from_orm(stock) for stock in stocks],
    )


@private_api.route("/stocks/bulk", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=StockIdsResponseModel, api=blueprint.pro_private_schema)
def upsert_stocks(body: StocksUpsertBodyModel) -> StockIdsResponseModel:
    try:
        offerer = offerers_repository.get_by_offer_id(body.offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        stocks = offers_api.upsert_stocks(body.offer_id, body.stocks, current_user)
    except offers_exceptions.BookingLimitDatetimeTooLate:
        raise ApiErrors(
            {"stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'événement"]},
            status_code=400,
        )

    return StockIdsResponseModel(
        stockIds=[StockIdResponseModel.from_orm(stock) for stock in stocks],
    )


@private_api.route("/stocks/<stock_id>", methods=["DELETE"])
@login_required
@spectree_serialize(response_model=StockIdResponseModel, api=blueprint.pro_private_schema)
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


@blueprint.pro_public_api_v2.route("/venue/<int:venue_id>/stocks", methods=["POST"])
@api_key_required
@spectree_serialize(
    on_success_status=204, on_error_statuses=[401, 404], api=blueprint.pro_public_schema_v2, tags=["API Stocks"]
)
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
    offerer_id = current_api_key.offererId  # type: ignore [attr-defined]
    venue = Venue.query.join(Offerer).filter(Venue.id == venue_id, Offerer.id == offerer_id).first_or_404()

    stock_details = _build_stock_details_from_body(body.stocks, venue.id)
    if any(stock.price is None for stock in body.stocks):
        # FIXME (dbaty, 2022-04-27): temporary log until we make the
        # price mandatory (if we decide to do so).
        logger.info("Stock API is used without a price", extra={"venue": venue_id})
    synchronize_stocks_job.delay(stock_details, venue.id)


def _build_stock_details_from_body(raw_stocks: List[UpdateVenueStockBodyModel], venue_id: int) -> list:
    stock_details = {}
    for stock in raw_stocks:
        stock_details[stock.ref] = {
            "products_provider_reference": stock.ref,
            "offers_provider_reference": stock.ref,
            "stocks_provider_reference": f"{stock.ref}@{str(venue_id)}",
            "available_quantity": stock.available,
            "price": stock.price,
        }

    return list(stock_details.values())


@private_api.route("/stocks/educational", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=StockIdResponseModel, api=blueprint.pro_private_schema)
def create_educational_stock(body: EducationalStockCreationBodyModel) -> StockIdResponseModel:
    try:
        offerer = offerers_repository.get_by_offer_id(body.offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        stock = offers_api.create_educational_stock(body, current_user)
    except educational_exceptions.EducationalStockAlreadyExists:
        raise ApiErrors(
            {"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"},
            status_code=400,
        )

    try:
        educational_api.create_collective_stock(body, current_user, legacy_id=stock.id)
    except exc.IntegrityError:
        logger.error(
            "Concurrent request trying to create educational stock for same offer", extra={"offerId": body.offer_id}
        )
        db.session.rollback()

    return StockIdResponseModel.from_orm(stock)


@private_api.route("/stocks/shadow-to-educational/<stock_id>", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=201, response_model=stock_serialize.PatchShadowStockIntoEducationalStockResponseModel
)
def transform_shadow_stock_into_educational_stock(
    stock_id: str, body: EducationalStockCreationBodyModel
) -> stock_serialize.PatchShadowStockIntoEducationalStockResponseModel:
    try:
        offerer = offerers_repository.get_by_offer_id(body.offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        stock = offers_api.transform_shadow_stock_into_educational_stock_and_create_collective_offer(
            dehumanize(stock_id), body, current_user  # type: ignore [arg-type]
        )
        collective_offer_id = educational_api.get_collective_offer_id_from_educational_stock(stock)
        serialized_stock = stock_serialize.PatchShadowStockIntoEducationalStockResponseModel.from_orm(stock)
        serialized_stock.offerId = humanize(collective_offer_id)

    except educational_exceptions.OfferIsNotShowcase:
        raise ApiErrors({"code": "OFFER_IS_NOT_SHOWCASE"}, status_code=400)

    return serialized_stock


@private_api.route("/stocks/educational/<stock_id>", methods=["PATCH"])
@login_required
@spectree_serialize(on_success_status=200, on_error_statuses=[400, 401, 404, 422], api=blueprint.pro_private_schema)
def edit_educational_stock(
    stock_id: str, body: EducationalStockEditionBodyModel
) -> stock_serialize.StockEditionResponseModel:
    try:
        stock = offers_repository.get_non_deleted_stock_by_id(dehumanize(stock_id))  # type: ignore [arg-type]
        offerer = offerers_repository.get_by_offer_id(stock.offerId)
    except offers_exceptions.StockDoesNotExist:
        raise ApiErrors({"educationalStock": ["Le stock n'existe pas"]}, status_code=404)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    collective_stock = educational_repository.get_collective_stock_from_stock_id(stock.id)

    try:
        stock = offers_api.edit_educational_stock(stock, body.dict(exclude_unset=True))
        if collective_stock:
            # FIXME (rpaoloni, 2022-03-09): raise exception if not collective_stock after the migration
            educational_api.edit_collective_stock(collective_stock, body.dict(exclude_unset=True))
        return stock_serialize.StockEditionResponseModel.from_orm(stock)
    except educational_exceptions.OfferIsNotEducational:
        raise ApiErrors(
            {"educationalStock": ["L'offre associée au stock n'est pas une offre éducationnelle"]}, status_code=422
        )
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
    except SQLAMultipleResultsFound:
        logger.exception(
            "Several non cancelled bookings found while trying to edit related educational stock",
            extra={"stock_id": stock_id},
        )
        raise ApiErrors(
            {
                "educationalStockEdition": [
                    "Plusieurs réservations non annulées portent sur ce stock d'une offre éducationnelle"
                ]
            },
            status_code=400,
        )


@private_api.route("/stocks/shadow/<stock_id>", methods=["PATCH"])
@login_required
@spectree_serialize(on_success_status=200, on_error_statuses=[400, 401, 404, 422])
def edit_shadow_stock(
    stock_id: str, body: offers_serialize.EducationalOfferShadowStockBodyModel
) -> stock_serialize.StockEditionResponseModel:
    try:
        stock = offers_repository.get_non_deleted_stock_by_id(dehumanize(stock_id))  # type: ignore [arg-type]
        offerer = offerers_repository.get_by_offer_id(stock.offerId)
        check_user_has_access_to_offerer(current_user, offerer.id)
        stock = offers_api.edit_shadow_stock(stock, body.dict(exclude_unset=True))
        educational_api.edit_collective_offer_template_from_stock(stock, body.dict(exclude_unset=True))

        return stock_serialize.StockEditionResponseModel.from_orm(stock)

    except offers_exceptions.StockDoesNotExist:
        raise ApiErrors({"code": "STOCK_NOT_FOUND"}, status_code=404)

    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"code": "OFFERER_NOT_FOUND"}, status_code=404)

    except educational_exceptions.OfferIsNotEducational:
        raise ApiErrors({"code": "OFFER_IS_NOT_EDUCATIONAL"}, status_code=400)

    except educational_exceptions.OfferIsNotShowcase:
        raise ApiErrors({"code": "OFFER_IS_NOT_SHOWCASE"}, status_code=400)

    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}, status_code=404)
