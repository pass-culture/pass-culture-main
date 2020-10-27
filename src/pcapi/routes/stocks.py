from flask import current_app as app, \
    jsonify, \
    request
from flask_login import current_user

from pcapi.connectors import redis
from pcapi.domain.allocine import get_editable_fields_for_allocine_stocks
from pcapi.domain.stocks import delete_stock_and_cancel_bookings, \
    have_beginning_date_been_modified
from pcapi.domain.user_emails import send_batch_cancellation_emails_to_users, \
    send_offerer_bookings_recap_email_after_offerer_cancellation, \
    send_batch_stock_postponement_emails_to_users
from pcapi.flask_app import private_api
from pcapi.models import Product
from pcapi.models import VenueSQLEntity
from pcapi.models.feature import FeatureToggle
from pcapi.models.mediation_sql_entity import MediationSQLEntity
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.user_offerer import RightsType
from pcapi.repository import offerer_queries, repository, feature_queries
from pcapi.core.bookings.repository import find_not_cancelled_bookings_by_stock
from pcapi.repository.offer_queries import get_offer_by_id
from pcapi.repository.stock_queries import find_stocks_with_possible_filters
from pcapi.routes.serialization import as_dict
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.mailing import MailServiceException, \
    send_raw_email
from pcapi.utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required
from pcapi.validation.routes.offers import check_offer_is_editable
from pcapi.validation.routes.stocks import check_request_has_offer_id, \
    check_dates_are_allowed_on_new_stock, \
    check_dates_are_allowed_on_existing_stock, \
    check_stock_is_not_imported, \
    check_stocks_are_editable_for_offer, \
    check_stock_is_updatable, \
    get_only_fields_with_value_to_be_updated, \
    check_only_editable_fields_will_be_updated

search_models = [
    # Order is important
    Product,
    VenueSQLEntity,
]


@private_api.route('/stocks', methods=['GET'])
@login_or_api_key_required
def list_stocks():
    filters = request.args.copy()
    return handle_rest_get_list(StockSQLEntity,
                                query=find_stocks_with_possible_filters(filters, current_user),
                                paginate=50)


@private_api.route('/stocks/<stock_id>',
           methods=['GET'],
           defaults={'mediation_id': None})
@private_api.route('/stocks/<stock_id>/<mediation_id>', methods=['GET'])
@login_or_api_key_required
def get_stock(stock_id, mediation_id):
    filters = request.args.copy()
    query = find_stocks_with_possible_filters(filters, current_user).filter_by(id=dehumanize(stock_id))

    if mediation_id is not None:
        mediation = load_or_404(MediationSQLEntity, mediation_id)

    if stock_id == '0':
        stock = {'id': '0',
                 'thing': {'id': '0',
                           'mediations': [mediation]}}
        return jsonify(stock)
    else:
        stock = query.first_or_404()
        return jsonify(as_dict(stock))


@private_api.route('/stocks', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_stock():
    request_data = request.json
    check_request_has_offer_id(request_data)
    offer_id = dehumanize(request_data.get('offerId'))
    offer = get_offer_by_id(offer_id)

    check_offer_is_editable(offer)

    check_dates_are_allowed_on_new_stock(request_data, offer)
    offerer = offerer_queries.get_by_offer_id(offer_id)
    ensure_current_user_has_rights(RightsType.editor, offerer.id)

    check_stocks_are_editable_for_offer(offer)

    new_stock = StockSQLEntity(from_dict=request_data)
    repository.save(new_stock)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=offer_id)

    return jsonify(as_dict(new_stock)), 201


@private_api.route('/stocks/<stock_id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_stock(stock_id):
    stock_data = request.json
    query = StockSQLEntity.queryNotSoftDeleted().filter_by(id=dehumanize(stock_id))
    stock = query.first_or_404()

    check_stock_is_updatable(stock)
    check_dates_are_allowed_on_existing_stock(stock_data, stock.offer)
    offerer_id = stock.offer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)

    stock_from_allocine_provider = stock.idAtProviders is not None

    if stock_from_allocine_provider:
        stock_editable_fields = get_editable_fields_for_allocine_stocks()
        existing_stock_data = jsonify(as_dict(stock)).json
        fields_to_update = get_only_fields_with_value_to_be_updated(existing_stock_data, stock_data)
        check_only_editable_fields_will_be_updated(fields_to_update, stock_editable_fields)

        stock.fieldsUpdated = fields_to_update

    previous_beginning_datetime = stock.beginningDatetime
    stock.populate_from_dict(stock_data)

    if have_beginning_date_been_modified(stock_data, previous_beginning_datetime):
        bookings = find_not_cancelled_bookings_by_stock(stock)
        if bookings:
            try:
                send_batch_stock_postponement_emails_to_users(bookings, send_email=send_raw_email)
            except MailServiceException as mail_service_exception:
                app.logger.error('Email service failure', mail_service_exception)

    repository.save(stock)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    return jsonify(as_dict(stock)), 200


@private_api.route('/stocks/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_stock(id):
    stock = load_or_404(StockSQLEntity, id)
    offerer_id = stock.offer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)
    bookings = delete_stock_and_cancel_bookings(stock)

    if bookings:
        try:
            send_batch_cancellation_emails_to_users(bookings, send_raw_email)
            send_offerer_bookings_recap_email_after_offerer_cancellation(bookings, send_raw_email)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    repository.save(stock, *bookings)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    return jsonify(as_dict(stock)), 200
