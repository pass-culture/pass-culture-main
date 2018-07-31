"""offers"""
from flask import current_app as app, jsonify, request
from flask_login import current_user

from models.event import Event
from models.event_occurrence import EventOccurrence
from models.offer import Offer
from models.stock import Stock
from models.offerer import Offerer
from models.pc_object import PcObject
from models.thing import Thing
from models.user_offerer import UserOfferer, RightsType
from models.venue import Venue
from utils.human_ids import dehumanize
from utils.includes import OFFER_INCLUDES
from utils.rest import delete, \
    ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required
from utils.search import get_search_filter


@app.route('/offers', methods=['GET'])
@login_or_api_key_required
def list_offers():
    offererId = dehumanize(request.args.get('offererId'))
    venueId = dehumanize(request.args.get('venueId'))
    query = Offer.query

    if venueId is not None:
        venue = Venue.query.filter_by(id=venueId)\
                           .first_or_404()
        ensure_current_user_has_rights(RightsType.editor,
                                       venue.managingOffererId)
        query = query.filter_by(venue=venue)
    elif offererId is not None:
        ensure_current_user_has_rights(RightsType.editor,
                                       offererId)
        query = query.join(Venue)\
                     .join(Offerer)\
                     .filter_by(id=offererId)
    elif not current_user.isAdmin:
        query = query.join(Venue)\
                     .join(Offerer)\
                     .join(UserOfferer)\
                     .filter(UserOfferer.user == current_user)

    search = request.args.get('search')
    if search is not None:
        query = query.outerjoin(Event)\
                     .outerjoin(Thing)\
                     .filter(get_search_filter([Event, Thing], search))

    return handle_rest_get_list(Offer,
                                include=OFFER_INCLUDES,
                                query=query,
                                page=request.args.get('page'),
                                paginate=10,
                                order_by='offer.id desc')


@app.route('/offers/<id>', methods=['GET'])
@login_or_api_key_required
def get_offer(id):
    offer = load_or_404(Offer, id)
    return jsonify(offer._asdict(include=OFFER_INCLUDES))

@app.route('/offers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_offer():
    ocas = Offer()
    venue = load_or_404(Venue, request.json['venueId'])
    ensure_current_user_has_rights(RightsType.editor,
                                   venue.managingOffererId)
    ocas.populateFromDict(request.json)
    PcObject.check_and_save(ocas)
    return jsonify(ocas._asdict(include=OFFER_INCLUDES)), 201

@app.route('/offers/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_offer(id):
    ocas = load_or_404(Offer, id)
    ensure_current_user_has_rights(RightsType.editor,
                                   ocas.venue.managingOffererId)
    return delete(ocas)
