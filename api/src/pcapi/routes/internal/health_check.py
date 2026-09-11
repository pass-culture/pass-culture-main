from pcapi.routes.apis import misc_blueprint
from pcapi.utils.health_checker import check_database_connection
from pcapi.utils.health_checker import read_version_from_file


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
