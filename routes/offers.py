from models.event import Event
from models.event_occurence import EventOccurence
from models.mediation import Mediation
from models.offer import Offer
from models.offerer import Offerer
from models.pc_object import PcObject
from models.thing import Thing
from models.venue import Venue

""" offers """
from pprint import pformat

from flask import current_app as app, jsonify, request
from sqlalchemy.exc import InternalError
from sqlalchemy.sql.expression import and_, or_

from models.api_errors import ApiErrors
from routes.offerers import check_offerer_user
from utils.human_ids import dehumanize
from utils.includes import OFFER_INCLUDES
from utils.rest import delete, \
    ensure_provider_can_update, \
    ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required
from utils.search import get_ts_queries, LANGUAGE

Event = Event
EventOccurence = EventOccurence
Mediation = Mediation
Offer = Offer
Offerer = Offerer
Thing = Thing
Venue = Venue

search_models = [
    #Order is important
    Thing,
    Venue,
    Event
]


def join_offers(query):
    for search_model in search_models:
        if search_model == Event:
            query = query.outerjoin(EventOccurence).outerjoin(search_model)
        else:
            query = query.outerjoin(search_model)
    return query


def query_offers(ts_query):
    return or_(
        *[
            model.__ts_vector__.match(
                ts_query,
                postgresql_regconfig=LANGUAGE
            )
            for model in search_models
        ]
    )


def make_offer_query():
    query = Offer.query
    # FILTERS
    filters = request.args.copy()
    # SEARCH
    if 'search' in filters and filters['search'].strip() != '':
        ts_queries = get_ts_queries(filters['search'])
        query = join_offers(query)\
                    .filter(and_(*map(query_offers, ts_queries)))
    if 'offererId' in filters:
        query = query.filter(Offer.offererId == dehumanize(filters['offererId']))
        check_offerer_user(query.first_or_404().offerer.query)
    # PRICE
    if 'hasPrice' in filters and filters['hasPrice'].lower() == 'true':
        query = query.filter(Offer.price != None)
    # RETURN
    return query


@app.route('/offers', methods=['GET'])
@login_or_api_key_required
def list_offers():
    return handle_rest_get_list(Offer,
                                query=make_offer_query(),
                                include=OFFER_INCLUDES,
                                paginate=50)

@app.route('/offers/<offer_id>',
           methods=['GET'],
           defaults={'mediation_id': None})
@app.route('/offers/<offer_id>/<mediation_id>', methods=['GET'])
def get_offer(offer_id, mediation_id):
    query = make_offer_query().filter_by(id=dehumanize(offer_id))
    if offer_id == '0':
        if mediation_id is None:
            return "", 404
        mediation = Mediation.query.filter_by(thingId=null,
                                              eventId=null,
                                              id=mediation_id)\
                                   .first_or_404()
        offer = {'id': '0',
                 'thing': {'id': '0',
                           'mediations': [mediation]}}
        return jsonify(offer)
    else:
        offer = query.first_or_404()
        return jsonify(offer._asdict(include=OFFER_INCLUDES))


@app.route('/offers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_offer():
    print('OFFER', request.json)
    new_offer = Offer(from_dict=request.json)
    PcObject.check_and_save(new_offer)
    return jsonify(new_offer._asdict(include=OFFER_INCLUDES)), 201


@app.route('/offers/<offer_id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_offer(offer_id):
    updated_offer_dict = request.json
    query = Offer.query.filter_by(id=dehumanize(offer_id))
    offer = query.first_or_404()
    ensure_provider_can_update(offer)
    offer.populateFromDict(updated_offer_dict)
    try:
        PcObject.check_and_save(offer)
    except InternalError as ie:
        if 'check_offer' in str(ie.orig):
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
                app.log.error("Unexpected error in patch offers: "+pformat(ie))
            return jsonify(ae.errors), 400
        else:
            raise ie
    return jsonify(offer._asdict(include=OFFER_INCLUDES)), 200

@app.route('/offers/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_offer(id):
    offer = load_or_404(Offer, id)
    if offer.eventOccurence:
        offererId = offer.eventOccurence.venue.managingOffererId
    else:
        offererId = offer.venue.managingOffererId
    ensure_current_user_has_rights(RightsType.editor,
                                   offererId)
    return delete(offer)
