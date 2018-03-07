from flask import current_app as app, jsonify, request
from flask_login import current_user
from sqlalchemy.sql.expression import and_, or_

from reco.offers import get_recommended_offers
from routes.offerers import check_offerer_user
from utils.human_ids import dehumanize
from utils.rest import ensure_provider_can_update,\
                       expect_json_data,\
                       get,\
                       login_or_api_key_required,\
                       update
from utils.search import get_ts_queries, LANGUAGE

Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Offer = app.model.Offer
Offerer = app.model.Offerer
Thing = app.model.Thing
Venue = app.model.Venue

include_joins = [
    {"key": 'eventOccurence',
     "sub_joins": [{"key": 'event',
                    "sub_joins": ['mediations']},
                   "venue"]},
    {"key": 'thing',
     "sub_joins": ['mediations']},
    "venue"
]

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


def refine_offers(query):
    # FILTERS
    filters = request.args.copy()
    # RECO
    if 'recommended' in filters:
        return get_recommended_offers(current_user)
    # SEARCH
    if 'search' in filters and filters['search'].strip() != '':
        ts_queries = get_ts_queries(filters['search'])
        query = join_offers(query)\
                    .filter(and_(*map(query_offers, ts_queries)))
    if 'offererId' in filters:
        query = query.filter(Offer.offererId == dehumanize(filters['offererId']))
        check_offerer_user(query.first_or_404().offerer)
    # PRICE
    if 'hasPrice' in filters and filters['hasPrice'].lower() == 'true':
        query = query.filter(Offer.price != None)
    # PAGINATE
    query = query.limit(50)
    # RETURN
    return query


@app.route('/offers', methods=['GET'])
@login_or_api_key_required
def list_offers():
    return get(Offer,
               include_joins=include_joins,
               refine=refine_offers)


@app.route('/offers/<offer_id>', methods=['GET'],
                                 defaults={'mediation_id': None})
@app.route('/offers/<offer_id>/<mediation_id>', methods=['GET'])
def get_offer(offer_id, mediation_id):
    query = Offer.query.filter_by(id=dehumanize(offer_id))
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
        return jsonify(offer._asdict(include_joins=include_joins))


@app.route('/offers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_offer():
    new_offer = Offer(from_dict=request.json)
    app.model.PcObject.check_and_save(new_offer)
    return jsonify(new_offer._asdict(include_joins=include_joins)), 201


@app.route('/offers/<offer_id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_offer(offer_id):
    updated_offer_dict = request.json
    query = Offer.query.filter_by(id=dehumanize(offer_id))
    offer = query.first_or_404()
    ensure_provider_can_update(offer)
    update(offer, updated_offer_dict)
    app.model.PcObject.check_and_save(offer)
    return jsonify(offer._asdict(include_joins=include_joins)), 200
