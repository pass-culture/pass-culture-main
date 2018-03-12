from flask import current_app as app, request
import simplejson as json

from utils.rest import handle_rest_get_list

thingModel = app.model.Thing

@app.route('/things/<ofType>:<identifier>', methods=['GET'])
def get_thing(ofType, identifier):
    query = thingModel.query.filter((thingModel.type == ofType) &
                                    (thingModel.idAtProviders == identifier))
    thing = query.first_or_404()
    return json.dumps(thing)

@app.route('/things', methods=['GET'])
def list_things():
    return handle_rest_get_list(thingModel)
