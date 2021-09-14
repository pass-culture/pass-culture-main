from flask import send_from_directory

from pcapi.flask_app import public_api


@public_api.route("/api/doc", strict_slashes=False)
def api_documentation():
    return send_from_directory("static/documentation", "index.html")


@public_api.route("/api/doc/<path:path>")
def static_files(path):
    if ".yaml" in path:
        return send_from_directory("documentation", path)

    return send_from_directory("static/documentation", path)
