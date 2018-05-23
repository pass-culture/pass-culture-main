"""occasions"""
from flask import current_app as app, jsonify
from flask_login import current_user

from utils.human_ids import dehumanize
from utils.includes import OCCASION_INCLUDES
from utils.rest import login_or_api_key_required
from utils.string_processing import inflect_engine

@app.route('/occasions', methods=['GET'])
@login_or_api_key_required
def list_occasions():
    event_ids = []
    occasions = []
    for offerer in current_user.offerers:
        for offer in offerer.offers:
            occasion = None
            if offer.eventOccurence and offer.eventOccurence.event.id not in event_ids:
                event_ids.append(offer.eventOccurence.event.id)
                occasion = offer.eventOccurence.event._asdict(include=OCCASION_INCLUDES)
                occasion['occasionType'] = 'events'
                occasions.append(occasion)
            elif offer.thing:
                occasion = offer.thing._asdict(include=OCCASION_INCLUDES)
                occasion['occasionType'] = 'things'
                occasions.append(occasion)
    return jsonify(occasions)

@app.route('/occasions/<occasionType>/<occasionId>', methods=['GET'])
@login_or_api_key_required
def get_occasion(occasionType, occasionId):
    model_name = inflect_engine.singular_noun(occasionType.title(), 1)
    occasion = app.model[model_name]\
                  .query.filter_by(id=dehumanize(occasionId)).one()
    return jsonify(occasion._asdict(include=OCCASION_INCLUDES))
