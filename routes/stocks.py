""" stocks """
from flask import current_app as app, jsonify, request
from flask_login import current_user

from domain.stocks import delete_stock_and_cancel_bookings
from domain.user_emails import send_batch_cancellation_emails_to_users, send_batch_cancellation_email_to_offerer
from models import Product
from models.mediation import Mediation
from models.pc_object import PcObject
from models.stock import Stock
from models.user_offerer import RightsType
from models.venue import Venue
from repository import offerer_queries
from repository.offer_queries import get_offer_by_id
from repository.stock_queries import find_stocks_with_possible_filters
from routes.serialization import as_dict
from utils.human_ids import dehumanize
from utils.mailing import MailServiceException, send_raw_email
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required
from validation.stocks import check_request_has_offer_id,\
    check_dates_are_allowed_on_new_stock, \
    check_dates_are_allowed_on_existing_stock,\
    check_stocks_are_editable_for_offer
from validation.offers import check_offer_is_editable

search_models = [
    # Order is important
    Product,
    Venue,
]


@app.route('/stocks', methods=['GET'])
@login_or_api_key_required
def list_stocks():
    filters = request.args.copy()
    return handle_rest_get_list(Stock, query=find_stocks_with_possible_filters(filters, current_user), paginate=50)


@app.route('/stocks/<stock_id>',
           methods=['GET'],
           defaults={'mediation_id': None})
@app.route('/stocks/<stock_id>/<mediation_id>', methods=['GET'])
@login_or_api_key_required
def get_stock(stock_id, mediation_id):
    filters = request.args.copy()
    query = find_stocks_with_possible_filters(filters, current_user).filter_by(id=dehumanize(stock_id))

    if mediation_id is not None:
        mediation = load_or_404(Mediation, mediation_id)

    if stock_id == '0':
        stock = {'id': '0',
                 'thing': {'id': '0',
                           'mediations': [mediation]}}
        return jsonify(stock)
    else:
        stock = query.first_or_404()
        return jsonify(as_dict(stock))


@app.route('/stocks', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_stock():
    request_data = request.json
    check_request_has_offer_id(request_data)
    offer_id = dehumanize(request_data.get('offerId', None))
    offer = get_offer_by_id(offer_id)

    check_offer_is_editable(offer)

    check_dates_are_allowed_on_new_stock(request_data, offer)
    offerer = offerer_queries.get_by_offer_id(offer_id)
    ensure_current_user_has_rights(RightsType.editor, offerer.id)

    check_stocks_are_editable_for_offer(offer)

    new_stock = Stock(from_dict=request_data)
    PcObject.save(new_stock)

    return jsonify(as_dict(new_stock)), 201


# TODO: Si changement d'horaires et qu'il y a des réservations il faut envoyer des mails !
# TODO: Interdire la modification d'évenements passés
@app.route('/stocks/<stock_id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_stock(stock_id):
    stock_data = request.json
    query = Stock.queryNotSoftDeleted().filter_by(id=dehumanize(stock_id))
    stock = query.first_or_404()
    check_offer_is_editable(stock.offer)
    check_dates_are_allowed_on_existing_stock(stock_data, stock.offer)
    offerer_id = stock.resolvedOffer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)

    check_stocks_are_editable_for_offer(stock.offer)

    stock.populate_from_dict(stock_data)
    PcObject.save(stock)

    return jsonify(as_dict(stock)), 200


@app.route('/stocks/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_stock(id):
    stock = load_or_404(Stock, id)
    check_offer_is_editable(stock.offer)
    offerer_id = stock.resolvedOffer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)
    bookings = delete_stock_and_cancel_bookings(stock)

    check_stocks_are_editable_for_offer(stock.offer)

    if bookings:
        try:
            send_batch_cancellation_emails_to_users(bookings, send_raw_email)
            send_batch_cancellation_email_to_offerer(bookings, send_raw_email)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    PcObject.save(stock, *bookings)

    return jsonify(as_dict(stock)), 200
