""" storage """
import os.path
from flask import current_app as app, jsonify, request, send_file

from utils.object_storage import local_path
from utils.string_processing import inflect_engine

print('LOCAL DEV MODE: Using disk based object storage')

GENERIC_STORAGE_MODEL_NAMES = [
    'Mediation'
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

"""
@app.route('/storage/<collectionName>/<id>', methods=['POST'])
def post_storage_file(collectionName, id):
    model_name = inflect_engine.singular_noun(collectionName.title(), 1)
    if model_name in GENERIC_STORAGE_MODEL_NAMES:
        model = app.model[model_name]
        entity = model.query.filter_by(id=id).first_or_404()
        entity.save_thumb(request.json)
    return jsonify({'text': "upload is a success"})
"""
