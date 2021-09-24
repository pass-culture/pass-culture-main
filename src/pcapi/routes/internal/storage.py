""" storage """
import os.path

from flask import send_file

from pcapi.core.object_storage.backends.local import LocalBackend
from pcapi.routes.apis import public_api


print("LOCAL DEV MODE: Using disk based object storage")


@public_api.route("/storage/<bucketId>/<path:objectId>")
def send_storage_file(bucketId, objectId):
    path = LocalBackend().local_path(bucketId, objectId)
    type_path = str(path) + ".type"
    if os.path.isfile(type_path):
        mimetype = open(type_path).read()
    else:
        return "file not found", 404
    return send_file(open(path, "rb"), mimetype=mimetype)
