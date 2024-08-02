""" storage """

from flask import Response
from flask import send_file

from pcapi.core.object_storage.backends.local import LocalBackend
from pcapi.routes.apis import public_api


@public_api.route("/storage/<bucket_id>/<path:object_id>")
def send_storage_file(bucket_id: str, object_id: str) -> Response:
    path = LocalBackend().local_path(bucket_id, object_id)
    type_path = path.parent / (path.name + ".type")
    if type_path.exists():
        mimetype = type_path.read_text()
    else:
        return Response(status=404, response="file not found")
    return send_file(path, mimetype=mimetype)
