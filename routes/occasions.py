"""occasions"""
from flask import current_app as app, jsonify, request
from flask_login import current_user

from utils.human_ids import dehumanize
from utils.includes import OCCASION_INCLUDES
from utils.rest import expect_json_data,\
                       login_or_api_key_required,\
                       update
from utils.string_processing import inflect_engine


def get_occasion_dict(occasion):
    return occasion._asdict(
        include=OCCASION_INCLUDES,
        has_dehumanized_id=True,
        has_model_name=True
    )

def create_event_occurence(json, occasion, offerer, venue):
    event_occurence = app.model.EventOccurence()
    event_occurence.event = occasion
    event_occurence.venue = venue
    update(event_occurence, json, **{ "skipped_keys": ['offer']})
    app.model.PcObject.check_and_save(event_occurence)

    offer = app.model.Offer()
    offer.eventOccurence = event_occurence
    offer.offerer = offerer
    update(offer, json['offer'][0])
    app.model.PcObject.check_and_save(offer)

@app.route('/occasions', methods=['GET'])
@login_or_api_key_required
def list_occasions():
    event_ids = []
    occasions = []
    for offerer in current_user.offerers:
        for managedVenue in offerer.managedVenues:
            for eventOccurence in managedVenue.eventOccurences:
                occasion = None
                if eventOccurence.event.id not in event_ids:
                    event_ids.append(eventOccurence.event.id)
                    occasion = get_occasion_dict(eventOccurence.event)
                    occasions.append(occasion)
            # TODO: find a similar method for things
    return jsonify(occasions)

@app.route('/occasions/<occasionType>/<occasionId>', methods=['GET'])
@login_or_api_key_required
def get_occasion(occasionType, occasionId):
    model_name = inflect_engine.singular_noun(occasionType.title(), 1)
    occasion = app.model[model_name]\
                  .query.filter_by(id=dehumanize(occasionId))\
                  .first_or_404()
    occasion_dict = get_occasion_dict(occasion)
    return jsonify(occasion_dict)


@app.route('/occasions/<occasionType>', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_occasion(occasionType):
    model_name = inflect_engine.singular_noun(occasionType.title(), 1)

    # CREATE THE OCCASION (EVENT OR THING)
    occasion = app.model[model_name]()
    occasion_dict = request.json['occasion']
    update(occasion, occasion_dict)
    app.model.PcObject.check_and_save(occasion)

    # DETERMINE OFFERER
    offerer = app.model.Offerer.query\
                       .filter_by(id=dehumanize(occasion_dict['offererId']))\
                       .first_or_404()

    # DETERMINE VENUE
    venue = app.model.Venue.query\
                           .filter_by(id=dehumanize(occasion_dict['venueId']))\
                           .first_or_404()

    # CREATE CORRESPONDING EVENT OCCURENCES
    event_occurences = request.json.get('eventOccurences')
    if event_occurences:
        for event_occurence_dict in event_occurences:
            create_event_occurence(
                event_occurence_dict,
                occasion,
                offerer,
                venue
            )

    return jsonify(get_occasion_dict(occasion)), 201

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
        update(occasion, occasion_dict)
        app.model.PcObject.check_and_save(occasion)
    first_occurence = occasion.occurences[0]
    venue = first_occurence.venue
    offerer = venue.managingOfferer

    # UPDATE CORRESPONDING EVENT OCCURENCES
    event_occurences = request.json.get('eventOccurences')
    if event_occurences:
        for event_occurence_dict in event_occurences:
            if event_occurence_dict.get('DELETE') == '_delete_':
                app.model.Offer\
                         .query\
                         .filter_by(eventOccurenceId=dehumanize(event_occurence_dict['id']))\
                         .delete()
                app.model.EventOccurence\
                         .query\
                         .filter_by(id=dehumanize(event_occurence_dict['id']))\
                         .delete()
                app.db.session.commit()
            else:
                create_event_occurence(
                    event_occurence_dict,
                    occasion,
                    offerer,
                    venue
                )
    return jsonify(get_occasion_dict(occasion)), 200
