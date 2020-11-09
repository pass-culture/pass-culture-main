from flask import current_app as app
from flask import jsonify
from flask import request
from flask_login import current_user

from pcapi.connectors import redis
from pcapi.core.bookings.repository import find_not_cancelled_bookings_by_stock
import pcapi.core.offers.api as offers_api
from pcapi.domain.allocine import get_editable_fields_for_allocine_stocks
from pcapi.domain.stocks import delete_stock_and_cancel_bookings
from pcapi.domain.stocks import have_beginning_date_been_modified
from pcapi.domain.user_emails import send_batch_cancellation_emails_to_users
from pcapi.domain.user_emails import send_batch_stock_postponement_emails_to_users
from pcapi.domain.user_emails import send_offerer_bookings_recap_email_after_offerer_cancellation
from pcapi.flask_app import private_api
from pcapi.models import Product
from pcapi.models import VenueSQLEntity
from pcapi.models.feature import FeatureToggle
from pcapi.models.mediation_sql_entity import MediationSQLEntity
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.user_offerer import RightsType
from pcapi.repository import feature_queries
from pcapi.repository import offerer_queries
from pcapi.repository import repository
from pcapi.repository.offer_queries import get_offer_by_id
from pcapi.repository.stock_queries import find_stocks_with_possible_filters
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization.stock_serialize import StockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockEditionBodyModel
from pcapi.routes.serialization.stock_serialize import StockResponseIdModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.mailing import MailServiceException
from pcapi.utils.mailing import send_raw_email
from pcapi.utils.rest import ensure_current_user_has_rights
from pcapi.utils.rest import handle_rest_get_list
from pcapi.utils.rest import load_or_404
from pcapi.utils.rest import login_or_api_key_required
from pcapi.validation.routes.stocks import check_dates_are_allowed_on_existing_stock
from pcapi.validation.routes.stocks import check_only_editable_fields_will_be_updated
from pcapi.validation.routes.stocks import check_stock_is_updatable
from pcapi.validation.routes.stocks import get_only_fields_with_value_to_be_updated


search_models = [
    # Order is important
    Product,
    VenueSQLEntity,
]


@private_api.route("/stocks", methods=["GET"])
@login_or_api_key_required
def list_stocks():
    filters = request.args.copy()
    return handle_rest_get_list(
        StockSQLEntity,
        query=find_stocks_with_possible_filters(filters, current_user),
        paginate=50,
    )


@private_api.route(
    "/stocks/<stock_id>", methods=["GET"], defaults={"mediation_id": None}
)
@private_api.route("/stocks/<stock_id>/<mediation_id>", methods=["GET"])
@login_or_api_key_required
def get_stock(stock_id, mediation_id):
    filters = request.args.copy()
    query = find_stocks_with_possible_filters(filters, current_user).filter_by(
        id=dehumanize(stock_id)
    )

    if mediation_id is not None:
        mediation = load_or_404(MediationSQLEntity, mediation_id)

    if stock_id == "0":
        stock = {"id": "0", "thing": {"id": "0", "mediations": [mediation]}}
        return jsonify(stock)
    else:
        stock = query.first_or_404()
        return jsonify(as_dict(stock))


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
    query = StockSQLEntity.queryNotSoftDeleted().filter_by(id=dehumanize(stock_id))
    stock = query.first_or_404()
    stock_data = body.dict(by_alias=True, exclude_unset=True)

    check_stock_is_updatable(stock)
    check_dates_are_allowed_on_existing_stock(stock_data, stock.offer)
    offerer_id = stock.offer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)

    stock_from_allocine_provider = stock.idAtProviders is not None

    if stock_from_allocine_provider:
        stock_editable_fields = get_editable_fields_for_allocine_stocks()
        existing_stock_data = jsonify(as_dict(stock)).json
        fields_to_update = get_only_fields_with_value_to_be_updated(
            existing_stock_data, stock_data
        )
        check_only_editable_fields_will_be_updated(
            fields_to_update, stock_editable_fields
        )

        stock.fieldsUpdated = fields_to_update

    previous_beginning_datetime = stock.beginningDatetime
    stock.populate_from_dict(stock_data)

    if have_beginning_date_been_modified(stock_data, previous_beginning_datetime):
        bookings = find_not_cancelled_bookings_by_stock(stock)
        if bookings:
            try:
                send_batch_stock_postponement_emails_to_users(
                    bookings, send_email=send_raw_email
                )
            except MailServiceException as mail_service_exception:
                app.logger.exception("Email service failure", mail_service_exception)

    repository.save(stock)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

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
            send_offerer_bookings_recap_email_after_offerer_cancellation(
                bookings, send_raw_email
            )
        except MailServiceException as e:
            app.logger.exception("Mail service failure", e)

    repository.save(stock, *bookings)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    return StockResponseIdModel.from_orm(stock)
