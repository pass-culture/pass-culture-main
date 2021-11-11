from flask import redirect
from flask import request
from werkzeug.wrappers import Response

from pcapi.utils.urls import get_webapp_for_native_redirection_url

from . import blueprint


@blueprint.native_v1.route("/redirect_to_native/<path:subpath>", methods=["GET"])
def redirect_to_native(subpath: str) -> Response:
    query_string = request.query_string.decode("utf8")
    return redirect(f"{get_webapp_for_native_redirection_url()}/{subpath}?{query_string}")
