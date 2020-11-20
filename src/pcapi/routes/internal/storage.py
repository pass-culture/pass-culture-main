""" storage """
import os.path

from flask import send_file

from pcapi.flask_app import public_api
from pcapi.utils.object_storage import local_path


print("LOCAL DEV MODE: Using disk based object storage")


@public_api.route("/storage/<bucketId>/<path:objectId>")
def send_storage_file(bucketId, objectId):
    path = local_path(bucketId, objectId)
    type_path = str(path) + ".type"
    if os.path.isfile(type_path):
        mimetype = open(type_path).read()
    else:
        return "file not found", 404
    return send_file(open(path, "rb"), mimetype=mimetype)
