import flask

from pcapi.routes.apis import public_api
from pcapi.utils.health_checker import check_database_connection
from pcapi.utils.health_checker import read_version_from_file


@public_api.route("/health/api", methods=["GET"])
def health_api() -> tuple[str, int]:
    output = read_version_from_file()
    return output, 200


@public_api.route("/health/database", methods=["GET"])
def health_database() -> tuple[str, int]:
    database_working = check_database_connection()
    return_code = 200 if database_working else 500
    output = read_version_from_file()
    return output, return_code


@public_api.route("/debug/client-ip", methods=["GET"])
def get_client_ip() -> tuple[str, int]:
    client_ip = flask.request.remote_addr or "unknown IP"
    return client_ip, 200
