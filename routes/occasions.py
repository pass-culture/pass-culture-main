"""occasions"""
from flask import current_app as app, jsonify, request
from flask_login import current_user

from utils.human_ids import dehumanize
from utils.includes import OCCASION_INCLUDES
from utils.rest import expect_json_data,\
                       login_or_api_key_required,\
                       update
from utils.string_processing import inflect_engine

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
                occasion['occasionType'] = 'evenements'
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
    occasion = app.model[model_name](from_dict=request.json)


    #current_user.

    return jsonify(occasion._asdict(include=OCCASION_INCLUDES)), 201

@app.route('/occasions/<occasionType>/<occasionId>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_occasion(occasionType, occasionId):
    model_name = inflect_engine.singular_noun(occasionType.title(), 1)
    occasion = app.model[model_name].query\
                                    .filter_by(id=dehumanize(occasionId))\
                                    .first_or_404()
    update(occasion, request.json)
    app.model.PcObject.check_and_save(occasion)
    return jsonify(occasion._asdict(include=OCCASION_INCLUDES, has_dehumanized_id=True)), 200
