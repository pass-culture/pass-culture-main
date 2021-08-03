from flask import redirect
from flask import request
from werkzeug.wrappers import Response

from pcapi import settings

from . import blueprint


@blueprint.native_v1.route("/redirect_to_native/<path:subpath>", methods=["GET"])
def redirect_to_native(subpath: str) -> Response:
    query_string = request.query_string.decode("utf8")
    return redirect(f"{settings.WEBAPP_FOR_NATIVE_REDIRECTION}/{subpath}?{query_string}")
