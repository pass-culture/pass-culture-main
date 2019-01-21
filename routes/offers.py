"""offers"""

from datetime import datetime

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.offers import check_digital_offer_consistency, InconsistentOffer
from models import ApiErrors, Offer, PcObject, Recommendation, \
    RightsType, Venue
from models.db import db
from repository import venue_queries, offer_queries
from repository.offer_queries import find_activation_offers, \
                                     find_by_venue_id_or_offerer_id_and_keywords_string_offers_where_user_has_rights
from utils.human_ids import dehumanize
from utils.includes import OFFER_INCLUDES
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404
from validation.offers import check_venue_exists_when_requested, check_user_has_rights_for_query


@app.route('/offers', methods=['GET'])
@login_required
def list_offers():
    offerer_id = dehumanize(request.args.get('offererId'))
    venue_id = dehumanize(request.args.get('venueId'))
    venue = venue_queries.find_by_id(venue_id)

    check_venue_exists_when_requested(venue, venue_id)
    check_user_has_rights_for_query(offerer_id, venue, venue_id)

    query = find_by_venue_id_or_offerer_id_and_keywords_string_offers_where_user_has_rights(
        offerer_id,
        venue,
        venue_id,
        current_user,
        request.args.get('keywords')
    )

    return handle_rest_get_list(Offer,
                                include=OFFER_INCLUDES,
                                query=query,
                                page=request.args.get('page'),
                                paginate=10,
                                order_by='offer.id desc')


@app.route('/offers/activation', methods=['GET'])
@login_required
def list_activation_offers():
    departement_code = current_user.departementCode
    query = find_activation_offers(departement_code)

    return handle_rest_get_list(
        Offer,
        include=OFFER_INCLUDES,
        query=query
    )


@app.route('/offers/<id>', methods=['GET'])
@login_required
def get_offer(id):
    offer = load_or_404(Offer, id)
    return jsonify(offer._asdict(include=OFFER_INCLUDES))


@app.route('/offers', methods=['POST'])
@login_required
@expect_json_data
def post_offer():
    offer = Offer()
    venue = load_or_404(Venue, request.json['venueId'])
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    offer.populateFromDict(request.json)

    if offer.thingId:
        try:
            check_digital_offer_consistency(offer, venue)
        except InconsistentOffer as e:
            errors = ApiErrors()
            errors.addError('global', e.message)
            raise errors

    PcObject.check_and_save(offer)
    return jsonify(offer._asdict(include=OFFER_INCLUDES)), 201


@app.route('/offers/<offer_id>', methods=['PATCH'])
@login_required
@expect_json_data
def update_offer(offer_id):
    offer = load_or_404(Offer, offer_id)
    ensure_current_user_has_rights(RightsType.editor, offer.venue.managingOffererId)
    # ensure only some properties can be modified
    newProps = dict()
    if 'isActive' in request.json:
        newProps['isActive'] = request.json['isActive']
    offer.populateFromDict(newProps)
    PcObject.check_and_save(offer)
    if 'isActive' in request.json \
            and not newProps['isActive']:
        Recommendation.query.filter((Recommendation.offerId == offer.id)
                                    & (Recommendation.validUntilDate > datetime.utcnow())) \
            .update({'validUntilDate': datetime.utcnow()})
        db.session.commit()
    return jsonify(offer._asdict()), 200
