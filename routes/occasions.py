"""occasions"""
from flask import current_app as app, jsonify, request
from flask_login import current_user

from utils.human_ids import dehumanize
from utils.includes import OCCASION_INCLUDES
from utils.rest import expect_json_data,\
                       login_or_api_key_required
from utils.string_processing import inflect_engine

OCCASION_KEYS = [
    'author',
    'description',
    'durationMinutes',
    'name',
    'performer',
    'stageDirector',
    'type'
]

def feed_occasion(mapper, json):
    for key in OCCASION_KEYS:
        if key in json:
            if key == 'type' and json[key] == '':
                mapper.type = None
            else:
                mapper.__setattr__(key, json[key])

EVENT_OCCURENCE_KEYS = [
    'beginningDatetime'
]

def feed_event_occurence(mapper, json):
    for key in EVENT_OCCURENCE_KEYS:
        mapper.__setattr__(key, json[key])

OFFER_KEYS = [
    'price'
]

def feed_offer(mapper, json):
    for key in OFFER_KEYS:
        mapper.__setattr__(key, json[key])

@app.route('/occasions', methods=['GET'])
@login_or_api_key_required
def list_occasions():
    event_ids = []
    occasions = []
    for offerer in current_user.offerers:
        for eventOccurence in offerer.venue.eventOccurences:
            occasion = None
            if eventOccurence.event.id not in event_ids:
                event_ids.append(eventOccurence.event.id)
                occasion = eventOccurence.event._asdict(
                    include=OCCASION_INCLUDES,
                    has_dehumanized_id=True
                )
                occasion['occasionType'] = 'events'
                occasions.append(occasion)
        # TODO: find a similar method for things
    return jsonify(occasions)

@app.route('/occasions/<occasionType>/<occasionId>', methods=['GET'])
@login_or_api_key_required
def get_occasion(occasionType, occasionId):
    model_name = inflect_engine.singular_noun(occasionType.title(), 1)
    occasion = app.model[model_name]\
                  .query.filter_by(id=dehumanize(occasionId)).one()
    return jsonify(occasion._asdict(include=OCCASION_INCLUDES, has_dehumanized_id=True))


@app.route('/occasions/<occasionType>', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_occasion(occasionType):
    model_name = inflect_engine.singular_noun(occasionType.title(), 1)

    print('request.json', request.json)

    # CREATE THE OCCASION (EVENT OR THING)
    occasion = app.model[model_name]()
    feed_occasion(occasion, request.json['occasion'])
    app.model.PcObject.check_and_save(occasion)

    # TODO: FIND THE CORRESPONDING VENUE
    offerer = current_user.offerers[0]
    venue = offerer.venue

    # CREATE CORRESPONDING EVENT OCCURENCES
    event_occurences = request.json.get('eventOccurences')
    if event_occurences:
        for event_occurence_dict in event_occurences:
            event_occurence = app.model.EventOccurence()
            event_occurence.event = occasion
            event_occurence.venue = venue
            feed_event_occurence(event_occurence, event_occurence_dict)
            app.model.PcObject.check_and_save(event_occurence)

            # CREATE OFFER
            offer = app.model.Offer()
            offer.eventOccurence = event_occurence
            offer.offerer = offerer
            feed_offer(offer, event_occurence_dict)
            app.model.PcObject.check_and_save(offer)

    return jsonify(occasion._asdict(include=OCCASION_INCLUDES)), 201

@app.route('/occasions/<occasionType>/<occasionId>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_occasion(occasionType, occasionId):
    model_name = inflect_engine.singular_noun(occasionType.title(), 1)

    # UPDATE THE OCCASION
    occasion = app.model[model_name].query\
                                    .filter_by(id=dehumanize(occasionId))\
                                    .first_or_404()
    occasion_dict = request.json.get('occasion')
    if occasion_dict:
        feed_occasion(occasion, occasion_dict)
        app.model.PcObject.check_and_save(occasion)

    # UPDATE CORRESPONDING EVENT OCCURENCES
    event_occurences = request.json.get('eventOccurences')
    if event_occurences:
        for event_occurence_dict in event_occurences:
            event_occurence = app.model.EventOccurence\
                          .query\
                          .filter_by(id=dehumanize(event_occurence_dict['id']))
            if event_occurence_dict['DELETE'] == '_delete_':
                app.model.Offer\
                         .query\
                         .filter_by(eventOccurenceId=dehumanize(event_occurence_dict['id']))\
                         .delete()
                event_occurence.delete()
                app.db.session.commit()
            else:
                event_occurence = event_occurence.first_or_404()
                feed_event_occurence(event_occurence, event_occurence_dict)
                app.model.PcObject.check_and_save(event_occurence)
    return jsonify(occasion._asdict(include=OCCASION_INCLUDES, has_dehumanized_id=True)), 200
