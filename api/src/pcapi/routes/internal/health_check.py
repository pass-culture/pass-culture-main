from pcapi.routes.apis import public_api
from pcapi.utils.health_checker import check_database_connection
from pcapi.utils.health_checker import read_version_from_file


@public_api.route("/health/api", methods=["GET"])
def health_api():  # type: ignore [no-untyped-def]
    output = read_version_from_file()
    return output, 200


@public_api.route("/health/database", methods=["GET"])
def health_database():  # type: ignore [no-untyped-def]
    database_working = check_database_connection()
    return_code = 200 if database_working else 500
    output = read_version_from_file()
    return output, return_code
