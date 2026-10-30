import json
import logging

from flask import request

from pcapi.routes.apis import misc_blueprint
from pcapi.utils.health_checker import check_database_connection
from pcapi.utils.health_checker import read_version_from_file


logger = logging.getLogger(__name__)


@misc_blueprint.route("/checktest", methods=["GET"])
def checktest() -> tuple[dict, int]:
    print(json.dumps(dict(request.headers), indent=2, sort_keys=True))
    logger.debug(
        "[Test Check] Check if client IP is available",
        extra={
            "headers": dict.fromkeys(request.headers.items()),
        },
    )
    output = dict(request.headers)
    return output, 200


@misc_blueprint.route("/health/api", methods=["GET"])
def health_api() -> tuple[str, int]:
    output = read_version_from_file()
    return output, 200


@misc_blueprint.route("/health/database", methods=["GET"])
def health_database() -> tuple[str, int]:
    database_working = check_database_connection()
    return_code = 200 if database_working else 500
    output = read_version_from_file()
    return output, return_code
