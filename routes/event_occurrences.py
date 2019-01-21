""" event_occurrences """
from flask import current_app as app, jsonify, request

from domain.discard_pc_objects import soft_delete_objects, cancel_bookings
from domain.user_emails import send_batch_cancellation_emails_to_users, send_batch_cancellation_email_to_offerer
from models import Event, EventOccurrence, Offer, PcObject, RightsType, Venue
from repository import booking_queries
from utils.human_ids import dehumanize
from utils.includes import EVENT_OCCURRENCE_INCLUDES
from utils.mailing import MailServiceException
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    load_or_404, \
    login_or_api_key_required, \
    handle_rest_get_list


@app.route('/eventOccurrences', methods=['GET'])
@login_or_api_key_required
def list_event_occurrences():
    return handle_rest_get_list(EventOccurrence)


@app.route('/eventOccurrences/<id>', methods=['GET'])
@login_or_api_key_required
def get_event_occurrence(id):
    eo = load_or_404(EventOccurrence, id)
    return jsonify(eo._asdict(include=EVENT_OCCURRENCE_INCLUDES))


@app.route('/eventOccurrences', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_event_occurrence():
    event = Event.query.join(Offer)\
                       .filter(Offer.id == dehumanize(request.json['offerId']))\
                       .first_or_404()
    event.ensure_can_be_updated()

    eo = EventOccurrence(from_dict=request.json)
    venue = load_or_404(Venue, request.json['venueId'])
    ensure_current_user_has_rights(RightsType.editor,
                                   venue.managingOffererId)

    PcObject.check_and_save(eo)
    return jsonify(eo._asdict(include=EVENT_OCCURRENCE_INCLUDES)), 201


@app.route('/eventOccurrences/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_event_occurrence(id):
    eo = load_or_404(EventOccurrence, id)

    eo.ensure_can_be_updated()

    ensure_current_user_has_rights(RightsType.editor,
                                   eo.offer.venue.managingOffererId)
    eo.populateFromDict(request.json)
    #TODO: Si changement d'horaires et qu'il y a des réservations il faut envoyer des mails !
    #TODO: Interdire la modification d'évenements passés
    PcObject.check_and_save(eo)

    return jsonify(eo._asdict(include=EVENT_OCCURRENCE_INCLUDES)), 200


@app.route('/eventOccurrences/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_event_occurrence(id):
    event_occurrence = load_or_404(EventOccurrence, id)
    ensure_current_user_has_rights(RightsType.editor,
                                   event_occurrence.offer.venue.managingOffererId)
    bookings = booking_queries.find_all_bookings_for_event_occurrence(event_occurrence)
    bookings = cancel_bookings(*bookings)
    soft_deleted_objects = soft_delete_objects(event_occurrence,*event_occurrence.stocks)
    if bookings:
        try:
            send_batch_cancellation_emails_to_users(bookings, app.mailjet_client.send.create)
            send_batch_cancellation_email_to_offerer(bookings, 'event_occurrence', app.mailjet_client.send.create)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    PcObject.check_and_save(*(bookings + soft_deleted_objects))

    return jsonify(event_occurrence._asdict()), 200
