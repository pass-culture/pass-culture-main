from flask import current_app as app

from pcapi.connectors import redis
import pcapi.core.offers.api as offers_api
from pcapi.domain.stocks import delete_stock_and_cancel_bookings
from pcapi.domain.user_emails import send_batch_cancellation_emails_to_users
from pcapi.domain.user_emails import send_offerer_bookings_recap_email_after_offerer_cancellation
from pcapi.flask_app import private_api
from pcapi.models import Offer
from pcapi.models import VenueSQLEntity
from pcapi.models.feature import FeatureToggle
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.user_offerer import RightsType
from pcapi.repository import feature_queries
from pcapi.repository import offerer_queries
from pcapi.repository import repository
from pcapi.repository.offer_queries import get_offer_by_id
from pcapi.routes.serialization.stock_serialize import StockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockEditionBodyModel
from pcapi.routes.serialization.stock_serialize import StockResponseIdModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.mailing import MailServiceException
from pcapi.utils.mailing import send_raw_email
from pcapi.utils.rest import ensure_current_user_has_rights
from pcapi.utils.rest import load_or_404
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
    stock = (
        StockSQLEntity.queryNotSoftDeleted()
        .filter_by(id=dehumanize(stock_id))
        .join(Offer, VenueSQLEntity)
        .first_or_404()
    )

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
    stock = load_or_404(StockSQLEntity, id)
    offerer_id = stock.offer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)
    bookings = delete_stock_and_cancel_bookings(stock)

    if bookings:
        try:
            send_batch_cancellation_emails_to_users(bookings, send_raw_email)
            send_offerer_bookings_recap_email_after_offerer_cancellation(bookings, send_raw_email)
        except MailServiceException as e:
            app.logger.exception("Mail service failure", e)

    repository.save(stock, *bookings)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    return StockResponseIdModel.from_orm(stock)
