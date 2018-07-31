""" stocks """
from pprint import pformat
from flask import current_app as app, jsonify, request
from sqlalchemy.exc import InternalError
from sqlalchemy.sql.expression import and_, or_

from models.api_errors import ApiErrors
from models.event import Event
from models.event_occurrence import EventOccurrence
from models.offer import Offer
from models.stock import Stock
from models.pc_object import PcObject
from models.thing import Thing
from models.user_offerer import RightsType
from models.venue import Venue
from routes.offerers import check_offerer_user
from utils.human_ids import dehumanize
from utils.rest import delete, \
    ensure_provider_can_update, \
    ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required
from utils.search import get_ts_queries, LANGUAGE

search_models = [
    #Order is important
    Thing,
    Venue,
    Event
]


def join_stocks(query):
    for search_model in search_models:
        if search_model == Event:
            query = query.outerjoin(EventOccurrence).join(Offer).outerjoin(search_model)
        else:
            query = query.join(Offer).outerjoin(search_model)
    return query


def query_stocks(ts_query):
    return or_(
        *[
            model.__ts_vector__.match(
                ts_query,
                postgresql_regconfig=LANGUAGE
            )
            for model in search_models
        ]
    )


def make_stock_query():
    query = Stock.query
    # FILTERS
    filters = request.args.copy()
    if 'offererId' in filters:
        query = query.filter(Stock.offererId == dehumanize(filters['offererId']))
        check_offerer_user(query.first_or_404().offerer.query)
    # PRICE
    if 'hasPrice' in filters and filters['hasPrice'].lower() == 'true':
        query = query.filter(Stock.price != None)
    # RETURN
    return query


@app.route('/stocks', methods=['GET'])
@login_or_api_key_required
def list_stocks():
    return handle_rest_get_list(Stock,
                                query=make_stock_query(),
                                paginate=50)

@app.route('/stocks/<stock_id>',
           methods=['GET'],
           defaults={'mediation_id': None})
@app.route('/stocks/<stock_id>/<mediation_id>', methods=['GET'])
def get_stock(stock_id, mediation_id):
    query = make_stock_query().filter_by(id=dehumanize(stock_id))
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
    print('STOCK', request.json)
    new_stock = Stock(from_dict=request.json)
    PcObject.check_and_save(new_stock)
    return jsonify(new_stock._asdict()), 201


@app.route('/stocks/<stock_id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_stock(stock_id):
    updated_stock_dict = request.json
    query = Stock.query.filter_by(id=dehumanize(stock_id))
    stock = query.first_or_404()
    ensure_provider_can_update(stock)
    stock.populateFromDict(updated_stock_dict)
    try:
        PcObject.check_and_save(stock)
    except InternalError as ie:
        if 'check_stock' in str(ie.orig):
            ae = ApiErrors()

            if 'available_too_low' in str(ie.orig):
                ae.addError('available', 'la quantité pour cette offre'
                                         + ' ne peut pas être inférieure'
                                         + ' au nombre de réservations existantes.')
            elif 'bookingLimitDatetime_too_late' in str(ie.orig):
                ae.addError('bookingLimitDatetime', 'la date limite de réservation'
                            + ' pour cette offre est postérieure à la date'
                            + ' de début de l\'évènement')
            else:
                app.log.error("Unexpected error in patch stocks: "+pformat(ie))
            return jsonify(ae.errors), 400
        else:
            raise ie
    return jsonify(stock._asdict()), 200

@app.route('/stocks/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_stock(id):
    stock = load_or_404(Stock, id)
    if stock.eventOccurrence:
        offererId = stock.eventOccurrence.venue.managingOffererId
    else:
        offererId = stock.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor,
                                   offererId)
    return delete(stock)
