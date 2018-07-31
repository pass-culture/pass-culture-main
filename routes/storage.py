""" storage """
import os.path
from flask import current_app as app, jsonify, request, send_file
from flask_login import current_user

from utils.human_ids import dehumanize
from utils.object_storage import local_path
from utils.string_processing import inflect_engine

print('LOCAL DEV MODE: Using disk based object storage')

GENERIC_STORAGE_MODEL_NAMES = [
    'Mediation',
    'User',
]

@app.route('/storage/<bucketId>/<path:objectId>')
def send_storage_file(bucketId, objectId):
    path = local_path(bucketId, objectId)
    type_path = str(path)+".type"
    if os.path.isfile(type_path):
        mimetype = open(type_path).read()
    else:
        return "file not found", 404
    return send_file(open(path, "rb"), mimetype=mimetype)


@app.route('/storage/thumb/<collectionName>/<id>/<index>', methods=['POST'])
def post_storage_file(collectionName, id, index):
    model_name = inflect_engine.singular_noun(collectionName.title(), 1)
    if model_name in GENERIC_STORAGE_MODEL_NAMES:
        model = app.model[model_name]
        entity = model.query.filter_by(id=dehumanize(id)).first_or_404()
        if model_name == 'Mediation':
            offerer = entity.occasion.eventOccurrences[0].offer[0].offerer
            if offerer not in current_user.offerers:
                return jsonify({
                    'text': "user is not allowed to add mediation in this offerer"
                }), 400
        entity.save_thumb(
            request.files['file'].read(),
            int(index)
        )
        return jsonify(entity._asdict()), 200
    else:
        return jsonify({'text': "upload is not authorized for this model"}), 400
