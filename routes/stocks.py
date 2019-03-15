""" stocks """
from flask import current_app as app, jsonify, request
from flask_login import current_user

from domain.discard_pc_objects import cancel_bookings
from domain.user_emails import send_batch_cancellation_emails_to_users, send_batch_cancellation_email_to_offerer
from models.event import Event
from models.offer import Offer
from models.pc_object import PcObject
from models.stock import Stock
from models.thing import Thing
from models.user_offerer import RightsType
from models.venue import Venue
from repository import booking_queries, offerer_queries, stock_queries
from repository.offer_queries import find_offer_by_id
from utils.human_ids import dehumanize
from utils.mailing import MailServiceException, send_raw_email
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required
from domain.keywords import LANGUAGE
from validation.stocks import check_request_has_offer_id, check_stock_has_dates_for_event_offer

search_models = [
    # Order is important
    Thing,
    Venue,
    Event
]


@app.route('/stocks', methods=['GET'])
@login_or_api_key_required
def list_stocks():
    filters = request.args.copy()
    return handle_rest_get_list(Stock,
                                query=stock_queries.find_stocks_with_possible_filters(filters, current_user),
                                paginate=50)


@app.route('/stocks/<stock_id>',
           methods=['GET'],
           defaults={'mediation_id': None})
@app.route('/stocks/<stock_id>/<mediation_id>', methods=['GET'])
@login_or_api_key_required
def get_stock(stock_id, mediation_id):
    filters = request.args.copy()
    query = stock_queries.find_stocks_with_possible_filters(filters, current_user).filter_by(id=dehumanize(stock_id))
    if stock_id == '0':
        stock = {'id': '0',
                 'thing': {'id': '0',
                           'mediations': [mediation]}}
        return jsonify(stock)
    else:
        stock = query.first_or_404()
        return jsonify(stock._asdict())


@app.route('/stocks', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_stock():
    request_data = request.json
    check_request_has_offer_id(request_data)
    offer_id = dehumanize(request_data.get('offerId', None))
    offer = find_offer_by_id(offer_id)
    check_stock_has_dates_for_event_offer(request_data, offer)
    offerer = offerer_queries.get_by_offer_id(offer_id)
    ensure_current_user_has_rights(RightsType.editor, offerer.id)

    new_stock = Stock(from_dict=request_data)
    stock_queries.save_stock(new_stock)
    return jsonify(new_stock._asdict()), 201



# @app.route('/eventOccurrences/<id>', methods=['PATCH'])
# @login_or_api_key_required
# @expect_json_data
# def edit_event_occurrence(id):
#     eo = load_or_404(EventOccurrence, id)
#
#     eo.ensure_can_be_updated()
#
#     ensure_current_user_has_rights(RightsType.editor,
#                                    eo.offer.venue.managingOffererId)
#     eo.populateFromDict(request.json)
#     #TODO: Si changement d'horaires et qu'il y a des réservations il faut envoyer des mails !
#     #TODO: Interdire la modification d'évenements passés
#     PcObject.check_and_save(eo)
#
#     return jsonify(eo._asdict(include=EVENT_OCCURRENCE_INCLUDES)), 200

@app.route('/stocks/<stock_id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_stock(stock_id):
    updated_stock_dict = request.json
    query = Stock.queryNotSoftDeleted().filter_by(id=dehumanize(stock_id))
    stock = query.first_or_404()
    offerer_id = stock.resolvedOffer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor, offerer_id)
    stock.populateFromDict(updated_stock_dict)
    stock_queries.save_stock(stock)
    return jsonify(stock._asdict()), 200


@app.route('/stocks/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_stock(id):
    stock = load_or_404(Stock, id)
    offerer_id = stock.resolvedOffer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor,
                                   offerer_id)
    stock.isSoftDeleted = True
    bookings = booking_queries.find_all_bookings_for_stock(stock)
    bookings = cancel_bookings(*bookings)
    if bookings:
        try:
            send_batch_cancellation_emails_to_users(bookings, send_raw_email)
            send_batch_cancellation_email_to_offerer(bookings, 'stock', send_raw_email)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    PcObject.check_and_save(*(bookings + [stock]))

    return jsonify(stock._asdict()), 200
