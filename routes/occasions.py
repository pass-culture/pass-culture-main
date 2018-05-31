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

def feed_occasion(occasion, json):
    for occasion_key in OCCASION_KEYS:
        if occasion_key in json:
            if occasion_key == 'type' and json[occasion_key] == '':
                occasion.type = None
            else:
                occasion.__setattr__(occasion_key, json[occasion_key])

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
    feed_occasion(occasion, request.json)
    app.model.PcObject.check_and_save(occasion)

    # TODO: FIND THE CORRESPONDING VENUE
    offerer = current_user.offerers[0]
    venue = offerer.venue

    # CREATE CORRESPONDING EVENT OCCURENCES
    dates = request.json.get('dates')
    if dates:
        for date in dates:
            event_occurence = app.model.EventOccurence()
            event_occurence.event = occasion
            event_occurence.beginningDatetime = date
            event_occurence.venue = venue
            app.model.PcObject.check_and_save(event_occurence)

            # CREATE OFFER
            offer = app.model.Offer()
            offer.eventOccurence = event_occurence
            offer.offerer = offerer
            offer.price = request.json['price']
            app.model.PcObject.check_and_save(offer)

    return jsonify(occasion._asdict(include=OCCASION_INCLUDES)), 201

@app.route('/occasions/<occasionType>/<occasionId>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_occasion(occasionType, occasionId):
    model_name = inflect_engine.singular_noun(occasionType.title(), 1)

    # GET THE OCCASION
    occasion = app.model[model_name].query\
                                    .filter_by(id=dehumanize(occasionId))\
                                    .first_or_404()
    feed_occasion(occasion, request.json)
    app.model.PcObject.check_and_save(occasion)

    # UPDATE CORRESPONDING EVENT OCCURENCES
    dates = request.json.get('dates')
    if dates:
        for date in dates:
            pass
            """
            event_occurence = app.model.EventOccurence()
            event_occurence.event = occasion
            event_occurence.beginningDatetime = date
            event_occurence.venue = venue
            app.model.PcObject.check_and_save(event_occurence)
            """

    return jsonify(occasion._asdict(include=OCCASION_INCLUDES, has_dehumanized_id=True)), 200
