from pcapi.flask_app import private_api
from pcapi.utils.health_checker import check_database_connection, read_version_from_file


@private_api.route('/health/api', methods=['GET'])
def health_api():
    output = read_version_from_file()
    return output, 200


@private_api.route('/health/database', methods=['GET'])
def health_database():
    database_working = check_database_connection()
    return_code = 200 if database_working else 500
    output = read_version_from_file()
    return output, return_code
