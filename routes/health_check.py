from flask import current_app as app

from utils.health_checker import check_database_connection, read_version_from_file


@app.route('/health/api', methods=['GET'])
def health_api():
    json = {'version': read_version_from_file()}
    return json, 200


@app.route('/health/database', methods=['GET'])
def health_database():
    database_working = check_database_connection()
    return_code = 200 if database_working else 500
    json = {'version': read_version_from_file()}
    return json, return_code
