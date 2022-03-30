""" storage """
from flask import send_file

from pcapi.core.object_storage.backends.local import LocalBackend
from pcapi.routes.apis import public_api


print("LOCAL DEV MODE: Using disk based object storage")


@public_api.route("/storage/<bucketId>/<path:objectId>")
def send_storage_file(bucketId, objectId):
    path = LocalBackend().local_path(bucketId, objectId)
    type_path = path.parent / (path.name + ".type")
    if type_path.exists():
        mimetype = type_path.read_text()
    else:
        return "file not found", 404
    with path.open("rb") as fp:
        return send_file(fp, mimetype=mimetype)
